"""Download only the trajectory files of the Furmanek et al. (2022) distance experiment.

The full dataset is one 2.9 GB zip, mostly EMG. This reads the zip's index
and the ten Trajectories.mat files (about 110 MB) with HTTP range requests,
so nothing else is downloaded.

Usage, from the repo root:
  python validation/fetch_furmanek2022.py [out_dir]     (default data/furmanek2022)
Then:
  python validation/furmanek2022.py data/furmanek2022/Full_Dataset/Dist_Pert/P*
"""

from __future__ import annotations

import fnmatch
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = "https://ndownloader.figshare.com/files/28215120"  # Full_Dataset.zip, doi:10.6084/m9.figshare.13377506.v2
PATTERN = "Full_Dataset/Dist_Pert/*/Trajectories.mat"
BLOCK = 1 << 20


class RemoteFile(io.RawIOBase):
    """A read-only, seekable view of a remote file. Each 1 MB block is fetched once."""

    def __init__(self, url: str):
        self.url, self.pos, self.cache, self.fetched = url, 0, {}, 0
        self.size = int(self._get(0, 0)[1])

    def _get(self, a: int, b: int) -> tuple[bytes, str]:
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={a}-{b}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            if r.status != 206:
                raise SystemExit(f"server ignored the range request (HTTP {r.status})")
            data = r.read()
            total = r.headers["Content-Range"].split("/")[1]
        self.fetched += len(data)
        return data, total

    def _block(self, k: int) -> bytes:
        if k not in self.cache:
            a = k * BLOCK
            self.cache[k] = self._get(a, min(a + BLOCK, self.size) - 1)[0]
        return self.cache[k]

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, off: int, whence: int = 0) -> int:
        self.pos = {0: off, 1: self.pos + off, 2: self.size + off}[whence]
        return self.pos

    def read(self, n: int = -1) -> bytes:
        n = self.size - self.pos if n is None or n < 0 else min(n, self.size - self.pos)
        out = bytearray()
        while len(out) < n:
            k, o = divmod(self.pos, BLOCK)
            chunk = self._block(k)[o : o + n - len(out)]
            out += chunk
            self.pos += len(chunk)
        return bytes(out)

    def readinto(self, b) -> int:
        data = self.read(len(b))
        b[: len(data)] = data
        return len(data)


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/furmanek2022")
    remote = RemoteFile(URL)
    with zipfile.ZipFile(remote) as z:
        for info in z.infolist():
            if not fnmatch.fnmatch(info.filename, PATTERN):
                continue
            dest = out / info.filename
            if dest.exists() and dest.stat().st_size == info.file_size:
                print("have", dest)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(info))
            remote.cache.clear()
            print("got ", dest)
    print(f"{remote.fetched / 1e6:.0f} MB downloaded")


if __name__ == "__main__":
    main()
