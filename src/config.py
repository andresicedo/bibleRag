import os


class Config:
    """Base configuration class."""
    APP_NAME = 'bibleRag'
    OPEN_AI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPEN_AI_MODEL = 'gpt-4o-2024-08-06'
    OPEN_AI_EMBEDDING_MODEL = 'text-embedding-3-small'
    LOG_LOCATION = '/logs'
    BIBLE_VERSION = 'kjv'


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