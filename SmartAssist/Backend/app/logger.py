import logging

log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers if imported multiple times
if not logger.hasHandlers():
    file_handler = logging.FileHandler("app.log")
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
