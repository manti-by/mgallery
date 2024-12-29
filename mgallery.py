#!/usr/bin/env python
import argparse
import logging.config

from mgallery.settings import LOGGING


logging.config.dictConfig(LOGGING)

parser = argparse.ArgumentParser(prog="python mgallery.py", description="Image deduplicate script.", add_help=True)

parser.add_argument(
    "-a",
    "--autodelete",
    action="store_true",
    default=False,
    help="Auto delete duplicates",
)
parser.add_argument(
    "-d",
    "--dump",
    action="store_true",
    default=False,
    help="Create db dump",
)
parser.add_argument(
    "-s",
    "--scan",
    action="store_true",
    default=False,
    help="Scan directory for images",
)
parser.add_argument(
    "-c",
    "--compare",
    action="store_true",
    default=False,
    help="Compare duplicated images",
)
parser.add_argument(
    "-r",
    "--rename",
    action="store_true",
    default=False,
    help="Rename images in the current directory",
)
parser.add_argument(
    "-o",
    "--resort",
    action="store_true",
    default=False,
    help="Resort images in the current directory",
)
parser.add_argument(
    "-t",
    "--thumbnails",
    action="store_true",
    default=False,
    help="Create thumbnails for duplicated images",
)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.autodelete:
        from mgallery.autodelete import run_autodelete

        run_autodelete()
    elif args.dump:
        from mgallery.dump import run_dump

        run_dump()
    elif args.scan:
        from mgallery.scanner import run_scanner

        run_scanner()
    elif args.compare:
        from mgallery.compare import run_compare

        run_compare()
    elif args.rename:
        from mgallery.rename import run_rename

        run_rename()
    elif args.resort:
        from mgallery.resort import run_resort

        run_resort()

    elif args.thumbnails:
        from mgallery.thumbnails import run_thumbnails

        run_thumbnails()
    else:
        parser.print_help()
