import logging
import os

def setup(path: str, level: int = logging.INFO):
    """Setup logging configuration."""
    if os.access(os.path.dirname(path), os.W_OK):
        os.makedirs(path, exist_ok=True)  # Ensure the directory exists
    else:
        raise OSError(f"Cannot create directory '{path}' as the file system is read-only.")
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(path + "/app.log"),
                            logging.StreamHandler()
                        ])
    logging.getLogger().setLevel(level)
    logging.info("Logging is set up at level: %s", logging.getLevelName(level))