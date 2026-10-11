# LawCodex — Estonia (Eesti)

Estonian national legislation **in force**, in its consolidated form (*terviktekst*), taken from
[Riigi Teataja](https://www.riigiteataja.ee) (the official State Gazette of Estonia) and converted
to Markdown. The Estonian text (`et/`) is the official one. The English translations published by
Riigi Teataja are in `en/`. They are **unofficial translations**: only the Estonian text is legally
binding.

Retrieved: **2026-10-11/12** (state of the Riigi Teataja database at that date).

## Contents

| Category | Directory | et files | en files |
|---|---|---:|---:|
| Constitution (*Eesti Vabariigi põhiseadus*) | `<lang>/pohiseadus/` | 1 | 1 |
| Laws (*seadused*) passed by the Riigikogu, the Supreme Council (*Ülemnõukogu*) or by referendum | `<lang>/seadused/<letter>/` | 995 | 275 |
| Government regulations (*Vabariigi Valitsuse määrused*) | `<lang>/maarused/vabariigi-valitsus/<year>/` | 960 | 12 |
| Ministers' regulations (*ministri määrused*), 34 issuing ministers (including former ministries) | `<lang>/maarused/<minister>/<year>/` | 2,735 | 45 |
| Regulations of the Governor of Eesti Pank (*Eesti Panga presidendi määrused*) | `<lang>/maarused/eesti-panga-president/<year>/` | 62 | 71 |
| **Total** | | **4,753** | **404** |

The Estonian set is everything that the Riigi Teataja search returns with the status "in force"
(*kehtivad*) in these four categories on the retrieval date. Of the 995 laws, 412 are consolidated
texts (*terviktekst*) of laws that have been amended. The other 583 are laws that were never amended,
whose original text is also the consolidated text (*algtekst-terviktekst*). Many of these are laws
ratifying international agreements. The `text_type` front-matter field gives this distinction.

The English set holds the 404 translations of laws and regulations that Riigi Teataja lists as in force
(status `IN_FORCE` in the English search). It does not include 8 translated government orders and
Riigikogu resolutions.

### Layout and file names

- `et/seadused/<letter>/<slug-of-title>.md`: laws are sharded by the first letter of the title (a
  GitHub directory shows at most 1,000 entries). For example, `et/seadused/k/karistusseadustik.md`
  is the Penal Code.
- `et/maarused/<issuer>/<year>/<slug-of-title>.md`: regulations are grouped by issuer and by the
  year they were adopted. The issuer is the authority named in the act (*väljaandja*), which may be a
  former minister title, e.g. `majandus-ja-kommunikatsiooniminister`.
- `en/` uses the same layout with slugs of the English titles. The issuer directory keeps the
  Estonian name, so it matches `et/`.
- Duplicate titles get a suffix: the regulation number (`-nr-12`) or the Riigi Teataja group id.

### File format

```markdown
---
title: "Karistusseadustik"
identifier: "109072026028"          # Riigi Teataja global id of this consolidated version (URL id)
rt_reference: "RT I, 09.07.2026, 28" # publication reference of this consolidated text
rt_original: "RT I 2001, 61, 364"    # publication of the original act
abbreviation: "KarS"
group_id: "..."                      # stable id of the act across versions (terviktekstiGrupiID)
type: act                            # constitution | act | regulation
issuer: "Riigikogu"
number: "35"                         # regulation number, when present
text_type: "terviktekst"             # or algtekst-terviktekst (never amended)
jurisdiction: ee
language: et
date: 2001-06-06                     # adoption date
last_amended: 2026-10-01             # start of validity of this consolidated version
status: in_force
source: "https://www.riigiteataja.ee/akt/109072026028"
retrieved: 2026-10-12
---
```

English files also have `translation: unofficial` and `translation_of` (the id of the Estonian
version that was translated). They also have a note under the title.

The structure of the act maps to headings: *osa* (part), *peatükk* (chapter), *jagu* (division),
*jaotis*/*alljaotis* (subdivisions) and § (*paragrahv*), down to `######`. Below that level, bold
labels are used. Subsections (*lõiked*, "(1)") and clauses (*punktid*, "1)") are paragraphs that
start with their official number. Amendment marks are kept as they appear on Riigi Teataja, e.g.
`[RT I, 12.07.2014, 1 - jõust. 01.01.2015]`, and so are correction notes (*veaparandus*). Notes on
EU law (*normitehnilised märkused*) and signatures come at the end. Tables are Markdown tables or
cleaned HTML. Annexes (*lisad*), which are PDF or image files embedded in the XML, are not converted.
They are listed under a final "Lisad" / "Annexes" heading, with links to the files on
riigiteataja.ee.

## Not covered

- Riigikogu resolutions (*otsused*), Government orders (*korraldused*) and other individual acts.
- Local government regulations (*KOV määrused*, ~11,000 in force).
- International agreements (*välislepingud*) as separate texts. Ratification laws are included, and
  agreement texts that are inline in them are included too.
- Repealed acts, earlier versions and future versions (*jõustuvad*) of acts.
- The content of annexes (PDF/images): linked, not converted.
- English: Riigi Teataja publishes translations of only part of the legislation. Translations that
  are not up to date with the current Estonian version are not in the in-force English list. These
  include, at retrieval time, the Penal Code (*Karistusseadustik*) and the Code of Criminal Procedure
  (*Kriminaalmenetluse seadustik*), so they are missing from `en/`.
- Two source texts are empty in the official XML (the `<sisu/>` element has no content), so their
  files only have metadata and a title: `et/maarused/haridus-ja-teadusminister/2011/kosejoe-kooli-pohimaarus.md`
  and `en/seadused/h/human-genes-research-act.md`.

## Sources

- Riigi Teataja public API used by the website (`https://www.riigiteataja.ee/public-api/api/v1/`):
  - `POST /otsing/tervik-tekst/<tab>` (tabs `seadused`, `vabariigi-valitsuse-maarused`,
    `ministri-maarused`, `eesti-panga-presidendi-maarused`; status `KEHTIVAD_KEHTETUTETA`)
    lists the acts in force.
  - `POST /en/search` (status `IN_FORCE`) lists the English translations in force.
  - `GET /akt/<id>/xml` and `GET /en/akt/<id>/xml` give the full XML of each act (schemas
    `tyviseadus_1_10.02.2010` and `maarus_1_10.02.2010`).
- Riigi Teataja also publishes bulk open data at <https://www.riigiteataja.ee/avaandmed/ERT/>
  (`xml.<year>.zip`, `xml.<year>.en.zip`). These yearly archives hold every version of every act
  (the 2026 archive alone is 43 GB, with 254,000 XML files) and give no in-force index. That is why
  this corpus uses the API to pick the current versions and downloads only those (about 1.4 GB of
  XML). The API returns the same XML documents.
- robots.txt was respected: it has no Crawl-delay, and none of the fetched paths are disallowed. The
  scripts used at most 3 concurrent requests with a descriptive User-Agent.

## Licence

Texts published in Riigi Teataja are official texts of the Republic of Estonia. Under § 5 of the
Estonian Copyright Act (*autoriõiguse seadus*), legislative and administrative acts and their
official translations are not protected by copyright. Riigi Teataja data is offered as open data.
The Markdown conversion and scripts in this repository are provided as is.

## Regenerating

```sh
pip install -r scripts/requirements.txt   # requests, lxml, beautifulsoup4, markdownify
cd scripts
python list_acts.py          # -> _raw/ee/list_et.json, list_en.json
python fetch.py              # -> _raw/ee/xml/{et,en}/<id>.xml (cached)
python convert.py et en      # -> et/, en/
```

Raw data goes in `/Users/magicaltux/projects/lawcodex/_raw/ee/`. Change `RAW` in
`scripts/common.py` to use another location. `scripts/remotezip.py` is a small helper that reads
single members of the remote bulk ZIP archives with HTTP range requests. The pipeline does not use it.
