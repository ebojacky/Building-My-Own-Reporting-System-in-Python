from pathlib import Path
from config import *
import logging

logger = logging.getLogger(__name__)


# Create App Directories
def create():
    try:
        dirs = [
            CDR_PATH,
            CDR_DONE_PATH,
            CDR_JSON_PATH,
            LOG_PATH,
            DB_PATH,
            TEMP_HTML,
        ]

        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    except Exception as e:
        logging.critical(str(e))


def create_these(dirs):
    try:
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    except Exception as e:
        logging.critical(str(e))
