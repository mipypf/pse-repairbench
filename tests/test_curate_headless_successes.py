from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "maintenance"))

from curate_headless_successes import copy_archive_without_pdfs  # noqa: E402


class CurateHeadlessSuccessesTest(unittest.TestCase):
    def test_copy_archive_excludes_pdf_and_preserves_flowsheet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            source = work / "source.zip"
            destination = work / "curated.zip"
            with ZipFile(source, "w") as archive:
                archive.writestr("source/abstract.PDF", b"logo-bearing abstract")
                archive.writestr("source/flowsheet.dwxmz", b"flowsheet")

            removed = copy_archive_without_pdfs(source, destination)

            self.assertEqual(removed, 1)
            with ZipFile(destination) as archive:
                self.assertEqual(archive.namelist(), ["source/flowsheet.dwxmz"])
                self.assertEqual(archive.read("source/flowsheet.dwxmz"), b"flowsheet")


if __name__ == "__main__":
    unittest.main()
