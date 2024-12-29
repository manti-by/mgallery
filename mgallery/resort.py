import logging
from datetime import datetime
from pathlib import Path

from mgallery.settings import GALLERY_PATH
from mgallery.utils import get_gallery_file_list


logger = logging.getLogger(__name__)


def month_to_season(month: int) -> str:
    if month in (1, 2, 12):
        return "Зима"
    if month in (3, 4, 5):
        return "Весна"
    if month in (6, 7, 8):
        return "Лето"
    return "Осень"


def get_path_from_filename(file_name: str) -> tuple[str, str, Path]:
    file_info = Path(file_name)
    target_datetime = datetime.strptime(file_info.stem[:19], "%Y-%m-%d_%H-%M-%S")
    season = month_to_season(target_datetime.month)
    return (
        f"{target_datetime.year} {season}",
        target_datetime.strftime("%Y-%m-%d"),
        file_info,
    )


def run_resort():
    for file_path in get_gallery_file_list():
        try:
            logger.info(f"Processing file {file_path}")

            counter = 0
            gallery, date, file_info = get_path_from_filename(file_path)
            target_directory = Path(GALLERY_PATH) / gallery / date
            target_directory.mkdir(parents=True, exist_ok=True)

            target_file_name = target_directory / f"{file_info.stem}{file_info.suffix}"
            while target_file_name.exists():
                counter += 1
                target_file_name = target_directory / f"{file_info.stem}-{counter}{file_info.suffix}"

            file_info.rename(target_file_name)
            logger.info(" - file is moved")
        except Exception as e:
            logger.error(e)
