# logging_config.py
import logging
import json

# Load logging configuration from the JSON file
def setup_logging():
    with open('logger_config.json', 'r') as f:
        logger_config = json.load(f)

    # Set up logging configuration
    logging.basicConfig(
        level=logger_config['LOGGING_CONFIG']['level'], 
        format=logger_config['LOGGING_CONFIG']['format'],  
        handlers=[
            logging.FileHandler(logger_config['LOGGING_CONFIG']['log_file']), 
            logging.StreamHandler() log to the console as well
        ]
    )
    logger = logging.getLogger() 

    return logger
