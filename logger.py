import logging
import os
from datetime import datetime, timedelta

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

def cleanup_old_logs(log_dir='logs', days=3):
    """Delete log files in log_dir older than 'days' days."""
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    for fname in os.listdir(log_dir):
        if fname.startswith('letterboxd-sync-') and fname.endswith('.log'):
            date_part = fname[len('letterboxd-sync-'):-len('.log')]
            try:
                file_date = datetime.strptime(date_part, '%Y%m%d')
                if file_date < cutoff:
                    os.remove(os.path.join(log_dir, fname))
            except Exception:
                continue 