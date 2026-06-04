import os


GALLERY_PATH = os.getenv("GALLERY_PATH", "/home/manti/www/mgallery/data")
THUMBNAILS_PATH = os.getenv("THUMBNAILS_PATH", "/var/mgallery/thumbnails")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://manti@127.0.0.1:5432/mgallery")

FILE_TYPES = ("arw", "dng", "jpg", "jpeg", "png", "webp", "gif")

NUM_PROCESSES = (os.cpu_count() or 1) - 1

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "%H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        }
    },
}
