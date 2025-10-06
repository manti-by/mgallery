import logging
import os

from mgallery.database import Database
from mgallery.settings import GALLERY_PATH, THUMBNAILS_PATH


logger = logging.getLogger(__name__)


def run_autodelete():
    database = Database()
    for _, images in database.duplicates().items():
        images = sorted(images, key=lambda x: x["size"], reverse=True)
        for image in images[1:]:
            database.delete(image["path"], image["name"])

            thumbnail_name = f"{THUMBNAILS_PATH}/{image['path']}/{image['name']}.jpg"
            if os.path.exists(thumbnail_name):
                os.remove(thumbnail_name)

            file_name = f"{GALLERY_PATH}/{image['path']}/{image['name']}"
            if os.path.exists(file_name):
                os.remove(file_name)
                logger.info(f"{file_name} is deleted")
