import logging
import os
from datetime import datetime

def setup_logging():
    """
    Set up comprehensive logging configuration for the entire application.
    This ensures all modules have consistent, detailed logging output.
    """
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'logs/processing_{timestamp}.log'
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        handlers=[
            # Console handler with colors and emojis
            logging.StreamHandler(),
            # File handler for persistent logging
            logging.FileHandler(log_filename, encoding='utf-8')
        ]
    )
    
    # Set specific loggers to INFO level
    loggers_to_set = [
        'src.create_chunks',
        'src.main',
        'src.graph_query',
        'src.document_sources.wikipedia',
        'src.document_sources.web_pages',
        'src.document_sources.local_file',
        'src.document_sources.gcs_bucket',
        'src.document_sources.s3_bucket',
        'src.document_sources.youtube',
        'src.llm',
        'src.graphDB_dataAccess',
        'src.make_relationships',
        'src.communities',
        'src.post_processing'
    ]
    
    for logger_name in loggers_to_set:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        # Prevent duplicate handlers
        if not logger.handlers:
            logger.addHandler(logging.StreamHandler())
            logger.addHandler(logging.FileHandler(log_filename, encoding='utf-8'))
    
    # Log startup message
    logging.info("🚀 LOGGING SYSTEM INITIALIZED")
    logging.info(f"📁 Log file: {log_filename}")
    logging.info(f"⏰ Timestamp: {timestamp}")
    logging.info("=" * 80)
    
    return log_filename

def get_logger(name):
    """
    Get a logger instance with the specified name.
    Ensures consistent logging configuration across all modules.
    """
    return logging.getLogger(name)

# Auto-setup logging when module is imported
if __name__ != "__main__":
    setup_logging()
