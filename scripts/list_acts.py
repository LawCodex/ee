#!/usr/bin/env python3
"""Enumerate the consolidated texts (terviktekstid) currently in force from the Riigi Teataja
search API and write _raw/ee/list_et.json and _raw/ee/list_en.json."""
import json, os, sys, time
from datetime import date
from common import API, RAW, request

# search tabs to collect (search API "sakk" names)
TABS = ["seadused", "vabariigi-valitsuse-maarused", "ministri-maarused",
        "eesti-panga-presidendi-maarused"]
PAGE = 30


def list_et():
    out = []
    for tab in TABS:
        seen = set()
        off = 0
        while True:
            body = {"general": {"searchAfter": off, "sort": "pealkiriSort", "sortAscending": True},
                    "precise": {"status": "KEHTIVAD_KEHTETUTETA"}}
            r = request("POST", f"{API}/otsing/tervik-tekst/{tab}", json=body).json()
            res = r.get("results") or []
            for x in res:
                if x["id"] not in seen:
                    seen.add(x["id"])
                    x["tab"] = tab
                    out.append(x)
            print(f"{tab} offset {off}: {len(res)} (total {len(seen)})", flush=True)
            if len(res) < PAGE:
                break
            off += PAGE
            time.sleep(0.3)
    return out


def list_en():
    out, seen, off = [], set(), 0
    today = date.today().isoformat()
    while True:
        body = {"general": {"searchAfter": off, "sort": "pealkiriSort", "sortAscending": True},
                "precise": {"status": "IN_FORCE", "inForceDate": today + "T00:00:00+03:00"}}
        r = request("POST", f"{API}/en/search", json=body).json()
        res = r.get("results") or []
        for x in res:
            if x["id"] not in seen:
                seen.add(x["id"])
                out.append(x)
        print(f"en offset {off}: {len(res)} (total {len(seen)} / {r.get('inForce')})", flush=True)
        if len(res) < PAGE:
            break
        off += PAGE
        time.sleep(0.3)
    return out


if __name__ == "__main__":
    os.makedirs(RAW, exist_ok=True)
    which = sys.argv[1:] or ["et", "en"]
    if "et" in which:
        json.dump(list_et(), open(f"{RAW}/list_et.json", "w"), ensure_ascii=False, indent=0)
    if "en" in which:
        json.dump(list_en(), open(f"{RAW}/list_en.json", "w"), ensure_ascii=False, indent=0)
