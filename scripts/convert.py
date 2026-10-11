#!/usr/bin/env python3
"""Convert the Riigi Teataja XML (tyviseadus / maarus schemas) downloaded by fetch.py into
Markdown files in the repository.

Usage: convert.py [et] [en]
"""
import html
import json
import os
import re
import sys
import unicodedata
from datetime import date

from lxml import etree

from common import RAW

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = date.today().isoformat()
SITE = "https://www.riigiteataja.ee"
PARSER = etree.XMLParser(huge_tree=True, remove_blank_text=False, resolve_entities=False,
                         no_network=True)

STRUCT = {"osa", "peatykk", "jagu", "jaotis", "alljaotis"}
TRANSL = str.maketrans({"õ": "o", "ä": "a", "ö": "o", "ü": "u", "š": "s", "ž": "z",
                        "Õ": "o", "Ä": "a", "Ö": "o", "Ü": "u", "Š": "s", "Ž": "z"})

L10N = {
    "et": {"inforce": "jõust.", "annexes": "Lisad", "annex": "Lisa", "notes": "Märkused",
           "sign": "Allkirjad", "corr": "Veaparandus"},
    "en": {"inforce": "entry into force", "annexes": "Annexes", "annex": "Annex",
           "notes": "Notes", "sign": "Signatures", "corr": "Correction"},
}


def ln(e):
    return etree.QName(e).localname if isinstance(e.tag, str) else None


def kid(e, name):
    for c in e:
        if ln(c) == name:
            return c
    return None


def kids(e, name):
    return [c for c in e if ln(c) == name]


def text_of(e):
    return "".join(e.itertext()) if e is not None else ""


def slugify(s, maxlen=90):
    s = s.translate(TRANSL)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    if len(s) > maxlen:
        s = s[:maxlen].rsplit("-", 1)[0]
    return s or "x"


def fmt_date(d):
    """'2025-04-11+03:00' -> '11.04.2025'"""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", d or "")
    return f"{m.group(3)}.{m.group(2)}.{m.group(1)}" if m else (d or "")


def iso_date(d):
    m = re.match(r"(\d{4}-\d{2}-\d{2})", d or "")
    return m.group(1) if m else None


# ---------------------------------------------------------------- inline text

MD_LINE_START = re.compile(r"^(\s*)([#>+*-]|\d+[.)]|=+|_{3,})(?=\s|$)")


def esc_text(s):
    s = s.replace("\\", "\\\\")
    s = re.sub(r"([*_`\[\]])", r"\\\1", s)
    s = re.sub(r"<(?=[a-zA-Z/!?])", "&lt;", s)
    return s


def esc_line_start(s):
    return MD_LINE_START.sub(lambda m: m.group(1) + re.sub(r"([#>+*\-.)=_])", r"\\\1", m.group(2), count=1), s)


def inline(e):
    """Render mixed content of a tavatekst/pealkiri-like element to Markdown."""
    out = [esc_text(e.text or "")]
    for c in e:
        n = ln(c)
        if n is None:  # comment / PI
            pass
        elif n == "reavahetus":
            out.append("\\\n")
        elif n in ("i", "em"):
            t = inline(c).strip()
            out.append(f"*{t}*" if t else "")
        elif n in ("b", "strong"):
            t = inline(c).strip()
            out.append(f"**{t}**" if t else "")
        elif n in ("sup", "sub", "u"):
            t = inline(c)
            out.append(f"<{n}>{t}</{n}>" if t else "")
        else:
            out.append(inline(c))
        out.append(esc_text(c.tail or ""))
    return "".join(out)


def html_fragment_to_md(s):
    """kuvatavNr etc. are CDATA HTML fragments such as '§ 38<sup>1</sup>.'"""
    try:
        frag = etree.fromstring(f"<x>{s}</x>")
        return inline(frag)
    except etree.XMLSyntaxError:
        return esc_text(re.sub(r"<[^>]+>", "", html.unescape(s)))


def clean_ws(s):
    s = s.replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\\\n *", "\\\n", s)
    return s.strip()


# ---------------------------------------------------------------- converter


class Converter:
    def __init__(self, lang, act_id, attach_base):
        self.lang = lang
        self.t = L10N[lang]
        self.id = act_id
        self.attach_base = attach_base
        self.blocks = []
        self.annexes = []
        self.notes = []

    def add(self, s):
        s = s.strip("\n")
        if s.strip():
            self.blocks.append(s)

    # --- amendment marks
    def amend_mark(self, mm):
        parts = []
        for av in kids(mm, "avaldamismarge"):
            osa = text_of(kid(av, "RTosa")).strip()
            kp = kid(av, "avaldamineKuupaev")
            art = text_of(kid(av, "RTartikkel")).strip()
            if kp is not None and text_of(kp).strip():
                ref = f"{osa}, {fmt_date(text_of(kp).strip())}, {art}"
            else:
                yr = text_of(kid(av, "RTaasta")).strip()
                nr = text_of(kid(av, "RTnr")).strip()
                ref = f"{osa} {yr}, {nr}, {art}".replace(" , ", ", ")
            parts.append(ref.strip(", "))
        s = "; ".join(parts)
        j = kid(mm, "joustumine")
        if j is not None and text_of(j).strip():
            s += f" - {self.t['inforce']} {fmt_date(text_of(j).strip())}"
        tv = kid(mm, "tavatekst")
        if tv is not None and text_of(tv).strip():
            t = clean_ws(inline(tv))
            if t.endswith(("-", "–")):  # e.g. "Kehtetu -" / "Repealed –": prefix
                s = f"{t} {s}"
            elif t.startswith(","):
                s += t
            else:
                s += " " + t
        s = s.strip()
        return f"\\[{s}\\]" if s else ""

    def correction(self, vp):
        txt = clean_ws(text_of(kid(vp, "veaparandusTekst")))
        d = fmt_date(text_of(kid(vp, "veaparandusKuupaev")).strip())
        return f"*\\[{esc_text(txt)} {d}\\]*".replace(" \\]", "\\]") if txt else ""

    def marks(self, e):
        """Amendment/correction marks that are direct children of e."""
        out = []
        for c in e:
            n = ln(c)
            if n == "muutmismarge":
                m = self.amend_mark(c)
                if m:
                    out.append(m)
                for vp in c.iter("{*}veaparandus"):
                    out.append(self.correction(vp))
            elif n == "veaparandus":
                out.append(self.correction(c))
        return [m for m in out if m]

    # --- content
    def sisutekst(self, st):
        """Render a sisuTekst element; returns list of blocks (first is the running text)."""
        runs, extra = [], []
        for c in st:
            n = ln(c)
            if n in ("tavatekst", "tavatekstStr"):
                runs.append(inline(c))
            elif n == "viide":
                kt = kid(c, "kuvatavTekst")
                runs.append(html_fragment_to_md(text_of(kt)) if kt is not None else "")
            elif n == "HTMLKonteiner":
                extra.append(self.html_block(text_of(c)))
            elif n == "tabel":
                extra.append(self.table(c))
            elif n == "fail":
                extra.append(self.file_link(c))
            elif n == "muutmismarge":
                m = self.amend_mark(c)
                if m:
                    extra.append(m)
                for vp in c.iter("{*}veaparandus"):
                    extra.append(self.correction(vp))
            elif n == "veaparandus":
                extra.append(self.correction(c))
            elif n is not None:
                runs.append(inline(c))
        text = clean_ws("".join(runs))
        return text, [x for x in extra if x]

    def file_link(self, f):
        name = f.get("failNimi") or "fail"
        if self.attach_base:
            return f"[{esc_text(name)}]({self.attach_base}{name})"
        return esc_text(name)

    def html_block(self, s):
        s = s.strip()
        if not s:
            return ""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            return s
        soup = BeautifulSoup(s, "html.parser")
        for tag in soup.find_all(True):
            for a in list(tag.attrs):
                if a not in ("colspan", "rowspan", "href", "src"):
                    del tag.attrs[a]
        if soup.find("table") is not None or soup.find("img") is not None:
            # keep as HTML, but make sure it is a single block without blank lines
            out = re.sub(r"\n\s*\n+", "\n", str(soup)).strip()
            return out
        from markdownify import markdownify
        md = markdownify(str(soup), heading_style="ATX", escape_asterisks=True,
                         escape_underscores=True)
        md = re.sub(r"\n{3,}", "\n\n", md).strip()
        return md

    def table(self, t):
        rows = []
        for tr in t.iter("{*}tr"):
            cells = []
            for tc in tr:
                if ln(tc) not in ("tc", "td", "th"):
                    continue
                parts = []
                for st in tc.iter("{*}sisuTekst"):
                    parts.append(self.sisutekst(st)[0])
                if not parts:
                    parts = [clean_ws(inline(tc))]
                cells.append(" ".join(p for p in parts if p).replace("|", "\\|").replace("\\\n", "<br>"))
            rows.append(cells)
        if not rows:
            return ""
        w = max(len(r) for r in rows)
        rows = [r + [""] * (w - len(r)) for r in rows]
        lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w]
        lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
        return "\n".join(lines)

    def heading(self, level, text):
        text = clean_ws(text).replace("\\\n", " ")
        if level <= 6:
            self.add("#" * level + " " + text)
        else:
            self.add(f"**{text}**")

    def struct_title(self, e, n):
        kn = kid(e, "kuvatavNr")
        nr = html_fragment_to_md(text_of(kn)).strip() if kn is not None and text_of(kn).strip() else ""
        if not nr:
            raw = text_of(kid(e, n + "Nr")).strip()
            if raw:
                nr = {"osa": f"{raw}. osa", "peatykk": f"{raw}. peatükk", "jagu": f"{raw}. jagu",
                      "jaotis": f"{raw}. jaotis", "alljaotis": f"{raw}. alljaotis"}[n] \
                    if self.lang == "et" else raw
        pk = kid(e, n + "Pealkiri")
        title = clean_ws(inline(pk)) if pk is not None else ""
        return " — ".join(x for x in (nr, title) if x) or n

    def numbered(self, e, n):
        """loige / alampunkt / punkt: '(1) text' paragraphs."""
        kn = kid(e, "kuvatavNr")
        nr = html_fragment_to_md(text_of(kn)).strip() if kn is not None else ""
        if not nr:
            raw = text_of(kid(e, n + "Nr")).strip()
            if raw:
                nr = {"loige": f"({raw})", "alampunkt": f"{raw})", "punkt": f"{raw}."}.get(n, raw)
        first = True
        for c in e:
            cn = ln(c)
            if cn == "sisuTekst":
                text, extra = self.sisutekst(c)
                if first:
                    text = f"{nr} {text}".strip() if nr else text
                    first = False
                if text:
                    self.add(esc_line_start(text) if not nr else self.prefix_safe(text))
                for x in extra:
                    self.add(x)
            elif cn in ("loige", "alampunkt", "punkt", "alapunkt"):
                if first and nr:
                    self.add(self.prefix_safe(nr))
                    first = False
                self.numbered(c, cn)
            elif cn == "muutmismarge":
                m = self.amend_mark(c)
                if m:
                    self.add(m)
                for vp in c.iter("{*}veaparandus"):
                    self.add(self.correction(vp))
            elif cn == "veaparandus":
                self.add(self.correction(c))
            elif cn in ("kuvatavNr", n + "Nr", None):
                pass
            elif cn == "normtehnmarkus":
                self.normnote(c)
            else:
                self.node(c, 6)
        if first and nr:
            self.add(self.prefix_safe(nr))

    @staticmethod
    def prefix_safe(text):
        # "1) foo" or "1. foo" would become an (auto-renumbered) Markdown list: escape
        return esc_line_start(text)

    def normnote(self, e):
        t = kid(e, "normtehnmarkusTekst")
        if t is None:
            t = e
        s = clean_ws(inline(t))
        if s:
            self.add(f"<sub>{s}</sub>" if False else f"*{s}*")

    def node(self, e, depth):
        n = ln(e)
        if n is None:
            return
        if n in STRUCT:
            self.heading(2 + depth, self.struct_title(e, n))
            for m in self.marks(e):
                self.add(m)
            for c in e:
                if ln(c) not in ("kuvatavNr", n + "Nr", n + "Pealkiri", "muutmismarge", "veaparandus"):
                    self.node(c, depth + 1)
        elif n == "paragrahv":
            kn = kid(e, "kuvatavNr")
            nr = html_fragment_to_md(text_of(kn)).strip() if kn is not None else ""
            if not nr:
                raw = text_of(kid(e, "paragrahvNr")).strip()
                nr = f"§ {raw}." if raw else ""
            pk = kid(e, "paragrahvPealkiri")
            title = clean_ws(inline(pk)) if pk is not None else ""
            self.heading(2 + depth, " ".join(x for x in (nr, title) if x))
            for c in e:
                cn = ln(c)
                if cn in ("kuvatavNr", "paragrahvNr", "paragrahvPealkiri", None):
                    continue
                if cn == "sisuTekst":
                    text, extra = self.sisutekst(c)
                    if text:
                        self.add(esc_line_start(text))
                    for x in extra:
                        self.add(x)
                else:
                    self.node(c, depth + 1)
        elif n in ("loige", "alampunkt", "punkt", "alapunkt"):
            self.numbered(e, n)
        elif n == "sisuTekst":
            text, extra = self.sisutekst(e)
            if text:
                self.add(esc_line_start(text))
            for x in extra:
                self.add(x)
        elif n == "preambul":
            for c in e:
                self.node(c, depth)
            for m in self.marks(e):
                self.add(m)
        elif n == "tavatekst":
            s = clean_ws(inline(e))
            if s:
                self.add(esc_line_start(s))
        elif n == "muutmismarge":
            m = self.amend_mark(e)
            if m:
                self.add(m)
            for vp in e.iter("{*}veaparandus"):
                self.add(self.correction(vp))
        elif n == "veaparandus":
            self.add(self.correction(e))
        elif n == "normtehnmarkus":
            self.normnote(e)
        elif n in ("HTMLKonteiner",):
            self.add(self.html_block(text_of(e)))
        elif n == "tabel":
            self.add(self.table(e))
        elif n == "viide":
            kt = kid(e, "kuvatavTekst")
            if kt is not None:
                self.add(html_fragment_to_md(text_of(kt)))
        elif n in ("kuvatavNr",) or n.endswith("Nr") or n.endswith("Pealkiri"):
            pass
        else:
            # unknown container: recurse
            for c in e:
                self.node(c, depth)

    def annex(self, lv):
        name = ""
        lp = kid(lv, "lisaPealkiri")
        if lp is not None:
            ln_ = kid(lp, "lisaNimi")
            name = clean_ws(inline(ln_ if ln_ is not None else lp))
        links = [self.file_link(f) for f in lv.iter("{*}fail")]
        texts = []
        for st in lv.iter("{*}sisuTekst"):
            t, extra = self.sisutekst(st)
            if t:
                texts.append(t)
            texts += [x for x in extra if not x.startswith("[") or "](" not in x]
        marks = []
        for mm in lv.iter("{*}muutmismarge"):
            m = self.amend_mark(mm)
            if m:
                marks.append(m)
        line = name or self.t["annex"]
        if links:
            line += " — " + ", ".join(links)
        self.annexes.append((line, texts, marks))

    def signatures(self, a):
        lines = []
        koht = text_of(kid(a, "allkiriKoht")).strip()
        for s in kids(a, "allkirjastaja"):
            nm = " ".join(x for x in (text_of(kid(s, "eesnimi")).strip(),
                                      text_of(kid(s, "perekonnanimi")).strip()) if x)
            am = text_of(kid(s, "ametinimetus")).strip()
            lines.append(esc_text(", ".join(x for x in (nm, am) if x)))
        if koht:
            lines.insert(0, esc_text(koht))
        return "\\\n".join(l for l in lines if l)

    def convert(self, root):
        sisu = kid(root, "sisu")
        name = kid(root, "aktinimi")
        title_notes = []
        if name is not None:
            for nm in name.iter("{*}normtehnmarkus"):
                t = kid(nm, "normtehnmarkusTekst")
                s = clean_ws(inline(t if t is not None else nm))
                if s:
                    title_notes.append(f"*{s}*")
            for vp in name.iter("{*}veaparandus"):
                c = self.correction(vp)
                if c:
                    title_notes.append(c)
        for x in title_notes:
            self.add(x)
        if sisu is not None:
            for c in sisu:
                self.node(c, 0)
        trailing_notes, sigs = [], []
        for c in root:
            n = ln(c)
            if n == "lisaViide":
                for lv in kids(c, "lisaViit") or [c]:
                    self.annex(lv)
            elif n == "normtehnmarkus":
                t = kid(c, "normtehnmarkusTekst")
                s = clean_ws(inline(t if t is not None else c))
                if s:
                    trailing_notes.append(s)
            elif n == "allkiri":
                s = self.signatures(c)
                if s:
                    sigs.append(s)
        if sigs:
            self.add("---")
            for s in sigs:
                self.add(s)
        if trailing_notes:
            self.add("---")
            for s in trailing_notes:
                self.add(esc_line_start(s))
        if self.annexes:
            self.add(f"## {self.t['annexes']}")
            for line, texts, marks in self.annexes:
                self.add("- " + line.replace("\\\n", " "))
                for t in texts:
                    self.add(t)
                for m in marks:
                    self.add(m)
        body = "\n\n".join(self.blocks)
        body = re.sub(r"\n{3,}", "\n\n", body)
        return body


# ---------------------------------------------------------------- metadata & paths


def meta(root):
    m = kid(root, "metaandmed")
    g = lambda *path: _path_text(m, path)
    d = {
        "valjaandja": g("valjaandja"),
        "dokumentLiik": g("dokumentLiik"),
        "tekstiliik": g("tekstiliik"),
        "lyhend": g("lyhend"),
        "aktikuupaev": g("vastuvoetud", "aktikuupaev"),
        "aktiNr": g("vastuvoetud", "aktiNr"),
        "kehtivuseAlgus": g("kehtivus", "kehtivuseAlgus"),
        "kehtivuseLopp": g("kehtivus", "kehtivuseLopp"),
        "globaalID": g("globaalID"),
        "grupiID": g("terviktekstiGrupiID"),
    }
    av = kid(m, "avaldamismarge")
    if av is not None:
        osa = text_of(kid(av, "RTosa")).strip()
        kp = text_of(kid(av, "avaldamineKuupaev")).strip()
        art = text_of(kid(av, "RTartikkel")).strip()
        if kp:
            d["rt"] = f"{osa}, {fmt_date(kp)}, {art}"
        else:
            d["rt"] = f"{osa} {text_of(kid(av, 'RTaasta')).strip()}, {text_of(kid(av, 'RTnr')).strip()}, {art}"
    vv = kid(m, "vastuvoetud")
    if vv is not None:
        av = kid(vv, "avaldamismarge")
        if av is not None:
            osa = text_of(kid(av, "RTosa")).strip()
            kp = text_of(kid(av, "avaldamineKuupaev")).strip()
            art = text_of(kid(av, "RTartikkel")).strip()
            if kp:
                d["rt_original"] = f"{osa}, {fmt_date(kp)}, {art}"
            elif osa:
                d["rt_original"] = f"{osa} {text_of(kid(av, 'RTaasta')).strip()}, {text_of(kid(av, 'RTnr')).strip()}, {art}"
    nimi = kid(kid(root, "aktinimi"), "nimi") if kid(root, "aktinimi") is not None else None
    d["title"] = clean_ws("".join(kid(nimi, "pealkiri").itertext())) if nimi is not None and kid(nimi, "pealkiri") is not None else ""
    return d


def _path_text(e, path):
    for p in path:
        if e is None:
            return ""
        e = kid(e, p)
    return text_of(e).strip() if e is not None else ""


def yq(s):
    return '"' + (s or "").replace("\\", "\\\\").replace('"', '\\"') + '"'


def front_matter(fields):
    lines = ["---"]
    for k, v in fields.items():
        if v is None or v == "":
            continue
        if isinstance(v, str) and k not in ("date", "last_amended", "retrieved", "status",
                                            "jurisdiction", "language", "type", "translation"):
            v = yq(v)
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def attach_base(lang, aid):
    s = str(aid)
    if len(s) == 12:
        p = f"{s[0:4]}/{s[4:8]}/{s[8:12]}/"
    else:
        p = None
    if p is None:
        return None
    return f"{SITE}/aktilisa/{p}" if lang == "et" else f"{SITE}/tolkelisa/{p}"


def first_letter_dir(slug):
    c = slug[0]
    return c if c.isalpha() else "0-9"


def plan_paths(lang, items):
    """Assign a repository path to each act. Returns {id: relpath}."""
    paths, used = {}, set()
    for it in items:
        m = it["meta"]
        title = m["title"] or it.get("title") or str(it["id"])
        is_law = m["dokumentLiik"] == "seadus"
        issuer = m["valjaandja"]
        if is_law and m.get("lyhend") == "PS" and issuer.startswith("Rahvahääletusel"):
            rel = f"{lang}/pohiseadus/pohiseadus.md"
        elif is_law:
            slug = slugify(title)
            rel = f"{lang}/seadused/{first_letter_dir(slug)}/{slug}.md"
        else:
            year = (m["aktikuupaev"] or "0000")[:4]
            slug = slugify(title, 80)
            rel = f"{lang}/maarused/{slugify(issuer, 60)}/{year}/{slug}.md"
        if rel in used:
            base = rel[:-3]
            suffix = m.get("aktiNr") and f"nr-{slugify(m['aktiNr'])}" or str(m.get("grupiID") or it["id"])
            rel = f"{base}-{suffix}.md"
            if rel in used:
                rel = f"{base}-{it['id']}.md"
        used.add(rel)
        paths[it["id"]] = rel
    return paths


def doc_type(m):
    if m["dokumentLiik"] == "seadus":
        if m.get("lyhend") == "PS" and m["valjaandja"].startswith("Rahvahääletusel"):
            return "constitution"
        return "act"
    return "regulation"


def run(lang):
    items = json.load(open(f"{RAW}/list_{lang}.json"))
    if lang == "en":
        # only acts and regulations (skip translated government orders and Riigikogu resolutions)
        items = [x for x in items if x.get("reportType") in ("act", "regulation")]
    ok = []
    for it in items:
        p = f"{RAW}/xml/{lang}/{it['id']}.xml"
        if not os.path.exists(p):
            print("missing", lang, it["id"])
            continue
        try:
            root = etree.parse(p, PARSER).getroot()
        except etree.XMLSyntaxError as e:
            print("bad xml", p, e)
            continue
        it["meta"] = meta(root)
        it["_root_path"] = p
        ok.append(it)
    # deterministic order: by title then id
    ok.sort(key=lambda x: (x["meta"]["title"].lower(), str(x["id"])))
    paths = plan_paths(lang, ok)
    written = []
    for it in ok:
        root = etree.parse(it["_root_path"], PARSER).getroot()
        m = it["meta"]
        conv = Converter(lang, it["id"], attach_base(lang, it["id"]))
        try:
            body = conv.convert(root)
        except Exception as e:
            print("convert error", it["id"], repr(e))
            raise
        title = m["title"] or it.get("title", "")
        fm = {
            "title": title,
            "identifier": str(m["globaalID"] or it["id"]),
            "rt_reference": m.get("rt"),
            "rt_original": m.get("rt_original"),
            "abbreviation": m.get("lyhend") or it.get("abbreviation"),
            "group_id": m.get("grupiID"),
            "type": doc_type(m),
            "issuer": m["valjaandja"],
            "number": m.get("aktiNr"),
            "text_type": m["tekstiliik"],
            "jurisdiction": "ee",
            "language": lang,
            "date": iso_date(m["aktikuupaev"]),
            "last_amended": iso_date(m["kehtivuseAlgus"]),
            "status": "in_force",
            "source": f"{SITE}/akt/{it['id']}" if lang == "et" else f"{SITE}/en/akt/{it['id']}",
            "retrieved": TODAY,
        }
        if lang == "en":
            fm["translation"] = "unofficial"
            if it.get("connectedTranslationId"):
                fm["translation_of"] = str(it["connectedTranslationId"])
        h1 = esc_text(title).replace("\\_", "_")
        parts = [front_matter(fm), "", f"# {h1}", ""]
        if lang == "en":
            parts += ["> Unofficial English translation published by Riigi Teataja. Only the "
                      "Estonian text is legally binding.", ""]
        parts.append(body)
        md = "\n".join(parts).rstrip() + "\n"
        rel = paths[it["id"]]
        out = os.path.join(REPO, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
        written.append({"id": it["id"], "path": rel, "type": fm["type"], "issuer": m["valjaandja"],
                        "title": title})
    json.dump(written, open(f"{RAW}/written_{lang}.json", "w"), ensure_ascii=False, indent=0)
    print(lang, "written", len(written))
    return written


if __name__ == "__main__":
    for lang in sys.argv[1:] or ["et", "en"]:
        run(lang)
