import json
import logging

from mgallery.database import Database


logger = logging.getLogger(__name__)


def run_dump():
    items = Database().all()
    with open("dump.json", "w") as f:
        f.write(json.dumps(items))
        logger.info(f"Dumped {len(items)} items")
