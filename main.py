# make.fun bounty entry: news-image-20261126
# "Sum up 26 November's world news in one image."
#
# The entry image is a 1024x1024 newspaper front page ("THE WORLD IN
# ONE DAY"), drawn with Python/PIL in build_image.py (included in this
# repo for provenance) from the verified news of Thursday 26 November
# 2026 -- 50 stories in 10 regions and 20 fields, every one happened or
# first reported on that day: a Thanksgiving storm floods the US East
# Coast and moves Macy's 100th parade to Saturday; Asian shares rebound
# (Nikkei +1.6%, Kospi +1.9%); EU leaders meet on a 45-billion-euro
# Ukraine loan and a budget showdown; Israel kills Hamas minister Khaled
# Abu Nada in Gaza; Nvidia halts chip-server shipments to four Southeast
# 13 die and 13 are trapped in a flooded Java gold mine; the Bank of
# Korea hikes its rate to 3.25%; plus 37 more stories in a numbered list,
# a UTC timeline, a stat strip and a pinned world map. Each of the 13
# biggest stories carries its own drawn scene and an OFFICIAL / CONFIRMED
# / REPORTED tag; a date check names the near-miss stories left out
# because they belong to other days (the US tariff proposal, the Asian
# chip crash and Pakistan's first astronaut are 25 November).
#
# The image itself is stored in this repo as entry.png (1024x1024, under
# 1 MiB). This program, Python 3.13 standard library only, copies it to
# /output/entry.png. No network, no timestamps, no randomness -- two runs
# write identical bytes.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "entry.png", OUT_DIR / "entry.png")


if __name__ == "__main__":
    main()
