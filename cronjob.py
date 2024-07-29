import os
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Missing argument")
        sys.exit(1)

    if sys.argv[1] == "monthly":
        monthly()


def monthly():
    here = Path(__file__).parent
    os.chdir(here)
    os.environ["PATH"] = f"./env/bin:{os.environ['PATH']}"

    os.system("flask infogreffe import-infos-cles 2022")
    os.system("flask infogreffe import-infos-cles 2023")
    os.system("flask infogreffe import-societes-radiees 2022")
    # os.system("./env/bin/flask infogreffe import-societes-radiees 2023")

    os.system("flask take-screenshots -o")

    os.system("flask sirene import-all")
    os.system("flask prepare update-all")


main()
