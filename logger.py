import logging
import os
from datetime import datetime, timedelta

def setup_logging(level=None, production_mode=False):
    """Setup logging configuration"""
    if level is None:
        # Use INFO for production, DEBUG for development
        level = logging.INFO if production_mode else logging.DEBUG
    
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
    
    # In production mode, suppress DEBUG messages from other modules
    if production_mode:
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def get_logger():
    """Get the configured logger"""
    return logging.getLogger(__name__)

def cleanup_old_logs(log_dir='logs', days=3):
    """Delete log files in log_dir older than 'days' days."""
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    deleted_count = 0
    
    for fname in os.listdir(log_dir):
        if fname.startswith('letterboxd-sync-') and fname.endswith('.log'):
            date_part = fname[len('letterboxd-sync-'):-len('.log')]
            try:
                file_date = datetime.strptime(date_part, '%Y%m%d')
                if file_date < cutoff:
                    os.remove(os.path.join(log_dir, fname))
                    deleted_count += 1
            except Exception:
                continue
    
    if deleted_count > 0:
        logger = get_logger()
        logger.info(f"Cleaned up {deleted_count} old log files") 