import os


class Config:
    """Base configuration class."""
    APP_NAME = 'bibleRag'
    DB_NAME = ""
    LOG_LOCATION = 'src/logs'
    BIBLE_VERSION = ''
    OPEN_AI_API_KEY = ''
    OPEN_AI_MODEL = ''
    OPEN_AI_EMBEDDING_MODEL = ''
    MONGO_CERT_PATH = ""
    MONGO_CHAT_COLLECTION = "chats"
    MONGO_PROMPT_COLLECTION = "prompts"
    MONGO_URI = ""
    OS_ENDPOINT = ""
    OS_CREDS = ['', '']


class LocalConfig(Config):
    """Configuration for local development."""
    DEBUG = True

    

class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True


def setup_config() -> Config:
    """Setup configuration for the Flask app."""
    env = os.environ.get('FLASK_ENV', 'local')

    config_mapping = {
        'dev': DevelopmentConfig
    }

    env_config = config_mapping.get(env, LocalConfig)
    env_config.ENV = env
    return env_config

env_config = setup_config()