import logging
from src import config
from pymongo import MongoClient, database

LOG = logging.getLogger(__name__)


CERT_PATH = config.env_config.MONGO_CERT_PATH
DB_NAME = config.env_config.DB_NAME
MONGO_URI = config.env_config.MONGO_URI


def initiate_mongo_client() -> MongoClient:
    """Initialize the MongoDB client with the provided URI and options."""
    LOG.info("Initializing MongoDB client")
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsCertificateKeyFile=CERT_PATH
        )
    return client

def get_bible_rag_db() -> database.Database:
    """Get the Bible RAG database."""
    LOG.info("Connecting to MongoDB at %s", MONGO_URI)
    db: database.Database = mongo_client[DB_NAME]
    return db

mongo_client: MongoClient = initiate_mongo_client()