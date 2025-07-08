import logging
import os
from datetime import datetime

def setup_logging(level=None):
    """Setup logging configuration"""
    if level is None:
        level = logging.INFO
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/letterboxd-sync-{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def get_logger():
    """Get the configured logger"""
    return logging.getLogger(__name__) 