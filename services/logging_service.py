import os
import logging
from logging.handlers import TimedRotatingFileHandler

# Ensure the logs directory exists
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Create and configure logger
logger = logging.getLogger("PrizePicksApiLogger")
logger.setLevel(logging.DEBUG)  # Or any other level

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler for daily rotation
# File handler for daily rotation
file_path = os.path.join(log_directory, 'my_app.log')
file_handler = TimedRotatingFileHandler(file_path, when='midnight', interval=1)
file_handler.suffix = '%Y-%m-%d'
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
    