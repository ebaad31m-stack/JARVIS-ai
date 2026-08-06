import logging
import os


LOG_FOLDER = "logs"

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)


logging.basicConfig(
    filename="logs/jarvis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_info(message):
    logging.info(message)


def log_error(message):
    logging.error(message)


def log_warning(message):
    logging.warning(message)