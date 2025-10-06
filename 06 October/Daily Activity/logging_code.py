import logging

logging.basicConfig(
	filename="app.log",
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.debug("This is a debug message")
logging.info("Application started")
logging.warning("Low memory warning")
logging.error("File not found error")
logging.critical("Critical system failure")