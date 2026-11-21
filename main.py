#!/usr/bin/env python3
"""Entry for make.fun news-image-20261121: sum up 21 November's world news
in one image.

The image is entry.png beside this file: a one-page newspaper front page
drawn by generate_image.py from verified reporting of Saturday 21 November
2026 (35 stories, 7 regions). This program only copies it to the grader's
output directory, so every run writes exactly the same bytes.

Standard library only; no network. Outside the grader's container,
MAKEFUN_OUTPUT_DIR stands in for /output:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> None:
    src = HERE / "entry.png"
    if not src.is_file():
        raise SystemExit(f"entry image missing: {src}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, OUT_DIR / "entry.png")


if __name__ == "__main__":
    main()
