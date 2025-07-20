# TODO Service to handle embedding operations for the Bible 
import logging
from typing import List
from src.models import RawDocument
from llama_index.core.schema import BaseNode, TextNode

LOG = logging.getLogger(__name__)

def embed_bible_nodes(processed_bible_nodes: List[TextNode], version: str):
    """Embed Bible nodes for the specified version."""
    LOG.info(f"Embedding {len(processed_bible_nodes)} nodes for Bible version: {version}")
    

def store_embedded_bible_nodes_in_vector_db(processed_bible_nodes: List[TextNode], version: str):
    """Store embedded Bible nodes in a vector database."""
    LOG.info(f"Storing {len(processed_bible_nodes)} embedded nodes for Bible version: {version}")

