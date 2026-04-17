import logging
import sys
from pathlib import Path

from core.config import settings


LOG_DIR = Path(__file__).parent
LOG_FILE = LOG_DIR / "app.log"

def setup_logger():
    logger = logging.getLogger("university_service")
    logger.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
