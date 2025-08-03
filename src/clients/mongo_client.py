import logging
from src import config
from pymongo import MongoClient, database
from pymongo.collection import Collection
from llama_index.storage.chat_store.mongo import MongoChatStore

LOG = logging.getLogger(__name__)


CERT_PATH = config.env_config.MONGO_CERT_PATH
DB_NAME = config.env_config.DB_NAME
MONGO_URI = config.env_config.MONGO_URI
MONGO_CHAT_COLLECTION = config.env_config.MONGO_CHAT_COLLECTION
MONGO_PROMPT_COLLECTION = config.env_config.MONGO_PROMPT_COLLECTION


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


def get_mongo_chat_store() -> MongoChatStore:
    return MongoChatStore(mongo_client=mongo_client, db_name=DB_NAME, collection_name=MONGO_CHAT_COLLECTION)


def get_mongo_prompt_collection() -> Collection:
    db: database.Database = get_bible_rag_db()
    return db[MONGO_PROMPT_COLLECTION]


mongo_client: MongoClient = initiate_mongo_client()