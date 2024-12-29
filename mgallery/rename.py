import logging
import os
from datetime import datetime
from pathlib import Path

import exifread

from mgallery.date_re import DATE_PARSERS
from mgallery.utils import get_gallery_file_list


logger = logging.getLogger(__name__)


def get_datetime_from_exif(name: str) -> datetime | None:
    with open(name, "rb") as f:
        exif_tags = exifread.process_file(f)
        if "EXIF DateTimeOriginal" in exif_tags:
            try:
                return datetime.strptime(str(exif_tags["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S")
            except ValueError as e:
                logger.warning(e)
            try:
                return datetime.strptime(str(exif_tags["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S.%f")
            except Exception as e:
                logger.warning(e)


def get_datetime_from_filename(name: str) -> datetime | None:
    for regex, func in DATE_PARSERS.items():
        try:
            matches = regex.search(name)
            if matches:
                return func(matches)
        except Exception as e:
            logger.error(e)


def run_rename():
    for file_name in get_gallery_file_list():
        try:
            logger.info(f"Processing file {file_name}")
            date_time = get_datetime_from_exif(file_name)

            if date_time is None:
                logger.warning(" - exif read failed, trying file name patterns")
                date_time = get_datetime_from_filename(file_name)

            if date_time is None:
                logger.warning(" - file name pattern not matched, using mtime")
                date_time = datetime.fromtimestamp(os.path.getmtime(file_name))

            counter = 0
            file_info = Path(file_name)
            target_name = f"{date_time.__format__('%Y-%m-%d_%H-%M-%S')}"
            target_file_name = file_info.parent / f"{target_name}{file_info.suffix}"
            while target_file_name.exists():
                counter += 1
                target_file_name = file_info.parent / f"{target_name}-{counter}{file_info.suffix}"

            file_info.rename(target_file_name)
            logger.info(" - file is renamed")
        except Exception as e:
            logger.error(e)
