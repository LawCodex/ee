#!/usr/bin/env python3
"""Download the XML of every act listed by list_acts.py into _raw/ee/xml/{et,en}/<id>.xml.
Cached: files already present are skipped."""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
from common import API, RAW, request

WORKERS = 3


def get(lang, aid):
    path = f"{RAW}/xml/{lang}/{aid}.xml"
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return "cached"
    url = f"{API}/akt/{aid}/xml" if lang == "et" else f"{API}/en/akt/{aid}/xml"
    try:
        r = request("GET", url, headers={"Accept": "application/octet-stream"})
    except Exception as e:
        print(f"FAIL {lang} {aid}: {e}", flush=True)
        return "fail"
    if not r.content.lstrip().startswith(b"<?xml"):
        print(f"NOT XML {lang} {aid}", flush=True)
        return "fail"
    tmp = path + ".part"
    open(tmp, "wb").write(r.content)
    os.replace(tmp, path)
    return "ok"


def main(langs):
    for lang in langs:
        os.makedirs(f"{RAW}/xml/{lang}", exist_ok=True)
        items = json.load(open(f"{RAW}/list_{lang}.json"))
        ids = [x["id"] for x in items]
        stats = {}
        with ThreadPoolExecutor(WORKERS) as ex:
            for i, st in enumerate(ex.map(lambda a: get(lang, a), ids)):
                stats[st] = stats.get(st, 0) + 1
                if i % 200 == 0:
                    print(lang, i, len(ids), stats, flush=True)
        print(lang, "done", stats, flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or ["et", "en"])
