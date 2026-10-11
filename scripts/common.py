"""Shared HTTP helpers for the Riigi Teataja public API."""
import time
import requests

UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
API = "https://www.riigiteataja.ee/public-api/api/v1"
RAW = "/Users/magicaltux/projects/lawcodex/_raw/ee"

_session = None


def session():
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({"User-Agent": UA, "Accept": "application/json"})
    return _session


def request(method, url, **kw):
    delay = 2
    for attempt in range(8):
        try:
            r = session().request(method, url, timeout=120, **kw)
            if r.status_code == 200:
                return r
            if r.status_code in (404, 400):
                r.raise_for_status()
            print(f"  HTTP {r.status_code} {url} (attempt {attempt})", flush=True)
        except requests.HTTPError:
            raise
        except Exception as e:  # network error
            print(f"  {e!r} {url} (attempt {attempt})", flush=True)
        time.sleep(delay)
        delay = min(delay * 2, 120)
    raise RuntimeError(f"giving up on {url}")
