# logging_config.py
import logging
import json

# Load logging configuration from the JSON file
def setup_logging():
    with open('logger_config.json', 'r') as f:
        logger_config = json.load(f)

    # Set up logging configuration
    logging.basicConfig(
        level=logger_config['LOGGING_CONFIG']['level'],  # Set the logging level (INFO in this case)
        format=logger_config['LOGGING_CONFIG']['format'],  # Specify the log message format
        handlers=[
            logging.FileHandler(logger_config['LOGGING_CONFIG']['log_file']),  # Log to the specified file
            logging.StreamHandler()  # Optionally, log to the console as well
        ]
    )
    logger = logging.getLogger()  # Get the logger object

    return logger
