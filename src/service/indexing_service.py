import logging
from typing import List
from src.models import RawDocument

from llama_index.core.schema import BaseNode, TextNode

LOG = logging.getLogger(__name__)


def chunk_all_documents(raw_bible: List[RawDocument], version: str) -> List[BaseNode]:
    """Chunk all documents into nodes."""
    LOG.info(f"Chunking {len(raw_bible)} pages for Bible version: {version}")
    nodes: List[BaseNode] = []
