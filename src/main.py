import logging 
from flask import Flask 
from src import config, logger

LOG = logging.getLogger(__name__)

def create_app() -> Flask:
    """Create and configure the Flask application."""
    LOG.info("Creating Flask application")
    
    env_config = config.setup_config()
    url_prefix = '/' + config.env_config.BIBLE_VERSION

    logger.setup(env_config.LOG_LOCATION)
    LOG.info("Setting up Flask app with environment: %s", env_config.__name__)

    flask_app: Flask = Flask(__name__, static_url_path=url_prefix + '/static', static_folder='static')
    flask_app.config.from_object(env_config)

    from src.routes.rag_routes import rag
    LOG.info("Registering RAG routes with URL prefix: %s", url_prefix)
    flask_app.register_blueprint(rag, url_prefix=url_prefix)

    from src.routes.prompting_routes import prompting
    LOG.info("Registering PROMPT routes with URL prefix %s", url_prefix)
    flask_app.register_blueprint(prompting, url_prefix=url_prefix)

    return flask_app