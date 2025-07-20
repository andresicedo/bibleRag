import logging

def setup(path: str, level: int = logging.INFO):
    """Setup logging configuration."""
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(path + "/app.log"),
                            logging.StreamHandler()
                        ])
    logging.getLogger().setLevel(level)
    logging.info("Logging is set up at level: %s", logging.getLevelName(level))