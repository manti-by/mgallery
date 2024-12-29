import logging
from concurrent import futures

from mgallery.database import Database
from mgallery.image import create_thumbnail
from mgallery.settings import NUM_PROCESSES


logger = logging.getLogger(__name__)


def get_duplicates_chunks(num_cores: int = NUM_PROCESSES) -> list[dict[str, dict]]:
    duplicates = Database().duplicates()
    logger.info(f"Found {len(duplicates)} duplicates")

    chunk_size = len(duplicates) // num_cores + 1
    return [
        dict(list(duplicates.items())[i : i + chunk_size])  # noqa
        for i in range(len(duplicates))[::chunk_size]
    ]


def create_thumbnails(duplicates: dict, process_index: int):
    counter = 0
    for _, images in duplicates.items():
        for image in images:
            if ".gif" in image["name"]:
                continue
            try:
                create_thumbnail(image["path"], image["name"])
            except Exception as e:
                logger.error(e)
                continue

            if (counter := counter + 1) % 500 == 0:
                logger.info(f"Processed {counter} thumbnails in thread #{process_index}")


def run_thumbnails(num_cores: int = NUM_PROCESSES):
    duplicates_chunks = get_duplicates_chunks(num_cores=num_cores)
    with futures.ProcessPoolExecutor(max_workers=num_cores) as executor:
        processes = []
        for i in range(num_cores):
            processes.append(executor.submit(create_thumbnails, duplicates_chunks[i], i))

    for _ in futures.as_completed(processes):
        """Wait while all processes will be completed"""
    logger.info("All threads are completed")
