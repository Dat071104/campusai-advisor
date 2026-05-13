"""Public Berkeley CS Guide source adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

BERKELEY_CS_GUIDE_HTML = "https://guide.berkeley.edu/undergraduate/degree-programs/computer-science/"
BERKELEY_CS_GUIDE_PDF = "https://guide.berkeley.edu/undergraduate/degree-programs/computer-science/computer-science.pdf"


@dataclass(frozen=True)
class BerkeleyFetchResult:
    html_path: str | None
    pdf_path: str | None
    notes: tuple[str, ...]


class BerkeleySourceAdapter:
    def __init__(self, raw_root: str | Path = "data/raw/documents/berkeley") -> None:
        self.raw_root = Path(raw_root)
        self.raw_root.mkdir(parents=True, exist_ok=True)

    def fetch(self, *, timeout: int = 20) -> BerkeleyFetchResult:
        notes: list[str] = []
        html_path = self.raw_root / "berkeley_cs_guide.html"
        pdf_path = self.raw_root / "berkeley_cs_guide.pdf"

        print("Downloading Berkeley CS guide HTML...", flush=True)
        html_ok = self._download(BERKELEY_CS_GUIDE_HTML, html_path, timeout=timeout)
        print("Downloading Berkeley CS guide PDF...", flush=True)
        pdf_ok = self._download(BERKELEY_CS_GUIDE_PDF, pdf_path, timeout=timeout, binary=True)

        if not html_ok:
            notes.append("HTML guide fetch failed or timed out; manual download may be needed.")
        if not pdf_ok:
            notes.append("PDF guide fetch failed or timed out; manual download may be needed.")

        return BerkeleyFetchResult(
            html_path=str(html_path) if html_ok else None,
            pdf_path=str(pdf_path) if pdf_ok else None,
            notes=tuple(notes),
        )

    def manual_download_instructions(self) -> str:
        return (
            "Manual download instructions:\n"
            f"1. Open {BERKELEY_CS_GUIDE_HTML}\n"
            f"2. Save the HTML page or download the PDF from {BERKELEY_CS_GUIDE_PDF}\n"
            f"3. Place the file in {self.raw_root}\n"
        )

    def _download(self, url: str, destination: Path, *, timeout: int, binary: bool = False) -> bool:
        try:
            request = Request(url, headers={"User-Agent": "CampusAI/1.0"})
            with urlopen(request, timeout=timeout) as response:
                content = response.read()
        except (URLError, TimeoutError, OSError) as exc:
            print(f"Fetch failed for {url}: {exc}", flush=True)
            return False

        if binary:
            destination.write_bytes(content)
        else:
            destination.write_text(content.decode("utf-8", errors="replace"), encoding="utf-8")
        return True
