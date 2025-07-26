import logging
import os
from dotenv import load_dotenv
# loading all environment variables
load_dotenv()

LOGGER_NAME = os.getenv('LOGGER_NAME','flask_app')
LOGS_LOC = os.getenv('LOGS_LOC','app.log')

def configure_logger():
    """Create and handling custom logger to application"""
    # Create a logger
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    # File handler for logging to a file
    file_handler = logging.FileHandler(LOGS_LOC)
    file_handler.setLevel(logging.ERROR)

    # Console handler for logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Formatter for log output
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = configure_logger()