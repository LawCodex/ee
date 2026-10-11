"""Minimal seekable HTTP-range file object, so zipfile can read members of a remote zip
without downloading the whole archive."""
import io, time, requests

UA = "LawCodex/1.0 (+https://github.com/LawCodex)"


class HTTPRangeFile(io.RawIOBase):
    def __init__(self, url, session=None, block=1 << 20):
        self.url = url
        self.s = session or requests.Session()
        self.s.headers["User-Agent"] = UA
        r = self.s.head(url, timeout=60)
        r.raise_for_status()
        self.size = int(r.headers["Content-Length"])
        self.pos = 0
        self.block = block
        self.cache = {}  # block index -> bytes (tiny LRU)
        self.bytes_fetched = 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        if whence == 0:
            self.pos = off
        elif whence == 1:
            self.pos += off
        else:
            self.pos = self.size + off
        return self.pos

    def _get(self, start, end):
        for attempt in range(6):
            try:
                r = self.s.get(self.url, headers={"Range": f"bytes={start}-{end - 1}"}, timeout=120)
                if r.status_code == 206:
                    self.bytes_fetched += len(r.content)
                    return r.content
                raise IOError(f"HTTP {r.status_code}")
            except Exception:
                if attempt == 5:
                    raise
                time.sleep(2 ** attempt)

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        out = bytearray()
        while n > 0:
            bi = self.pos // self.block
            data = self.cache.get(bi)
            if data is None:
                st = bi * self.block
                data = self._get(st, min(st + self.block, self.size))
                if len(self.cache) > 64:
                    self.cache.pop(next(iter(self.cache)))
                self.cache[bi] = data
            off = self.pos - bi * self.block
            chunk = data[off:off + n]
            out += chunk
            self.pos += len(chunk)
            n -= len(chunk)
        return bytes(out)

    def readinto(self, b):
        d = self.read(len(b))
        b[:len(d)] = d
        return len(d)
