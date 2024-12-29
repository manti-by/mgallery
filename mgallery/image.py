import logging.config
import os

import cv2
import rawpy
from PIL import Image

from mgallery.database import Database
from mgallery.phash import get_image_phash
from mgallery.settings import GALLERY_PATH, THUMBNAILS_PATH


logger = logging.getLogger(__name__)


def process_raw_image(database: Database, path: str, name: str, size: int):
    try:
        with rawpy.imread(f"{GALLERY_PATH}/{path}/{name}") as raw:
            rgb_image = raw.postprocess()
            bgr_image = rgb_image[:, :, ::-1]
            phash = get_image_phash(bgr_image)
            width, height = rgb_image.shape[0], rgb_image.shape[1]
        database.create(path=path, name=name, width=width, height=height, phash=phash, size=size)
    except Exception as e:
        logger.error(e)


def process_rgb_image(database: Database, path: str, name: str, size: int):
    try:
        width = height = phash = None
        image = cv2.imread(f"{GALLERY_PATH}/{path}/{name}")
        if image is not None:
            phash = get_image_phash(image)
            width, height = image.shape[0], image.shape[1]
        database.create(path=path, name=name, width=width, height=height, phash=phash, size=size)
    except Exception as e:
        logger.error(e)


def process_image(database: Database, path: str, name: str):
    size = os.path.getsize(f"{GALLERY_PATH}/{path}/{name}")
    if name.split(".")[-1].lower() in ("arw", "dng"):
        process_raw_image(database, path, name, size)
    else:
        process_rgb_image(database, path, name, size)


def create_thumbnail(path: str, name: str, size: int = 128, force: bool = False) -> str:
    source = f"{GALLERY_PATH}/{path}/{name}"
    thumbnail = f"{THUMBNAILS_PATH}/{path}/{name}.jpg"
    if os.path.exists(thumbnail) and not force:
        return thumbnail

    os.makedirs(f"{THUMBNAILS_PATH}/{path}", exist_ok=True)
    if name.split(".")[-1].lower() in ("arw", "dng"):
        with rawpy.imread(source) as raw:
            image = Image.fromarray(raw.postprocess())
    else:
        image = Image.open(source)

    image.thumbnail((size, size))
    image.save(thumbnail, quality=80, optimize=True)
    return thumbnail


def process_image_list(files: list, existing_images: list):
    database = Database()
    for current_file in files:
        name = os.path.basename(current_file)
        path = str(os.path.dirname(current_file).replace(GALLERY_PATH, ""))
        if f"{path}/{name}" not in existing_images:
            process_image(database, path, name)
            logger.debug(f"Added image {name} to gallery {path or 'root'}")
