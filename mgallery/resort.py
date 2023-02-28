from pathlib import Path

import exifread
import logging

from datetime import datetime

from mgallery.date_re import DATE_PARSERS
from mgallery.utils import get_gallery_file_list

logger = logging.getLogger(__name__)


def get_datetime_from_exif(name: str) -> datetime | None:
    with open(name, "rb") as f:
        exif_tags = exifread.process_file(f)
        if "EXIF DateTimeOriginal" in exif_tags:
            return datetime.strptime(
                str(exif_tags["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S"
            )


def get_datetime_from_filename(name: str) -> datetime | None:
    for regex, func in DATE_PARSERS.items():
        try:
            matches = regex.search(name)
            if matches:
                return func(matches)
        except Exception as e:
            logger.error(e)


def run_resort():
    for file_name in get_gallery_file_list():
        try:
            logger.info(f"Processing file {file_name}")

            date_time = get_datetime_from_exif(file_name)
            if date_time is None:
                logger.warning(" - exif read failed, trying file name patterns")
                date_time = get_datetime_from_filename(file_name)

            if date_time is None:
                logger.error(" - file name pattern not matched, skipping")
                continue

            counter = 0
            file_info = Path(file_name)
            target_name = f"{date_time.__format__('%Y-%m-%d_%H-%M-%S')}{file_info.suffix}"
            target_file_name = file_info.parent / f"{target_name}"
            while target_file_name.exists():
                counter += 1
                target_name = f"{date_time.__format__('%Y-%m-%d_%H-%M-%S')}-{counter}{file_info.suffix}"
                target_file_name = file_info.parent / f"{target_name}"

            file_info.rename(target_file_name)
            logger.info(" - file is renamed")
        except Exception as e:
            logger.error(e)