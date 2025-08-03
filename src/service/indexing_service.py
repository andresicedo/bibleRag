import logging
from typing import List
from src.models import RawDocument

from llama_index.core.schema import BaseNode, TextNode

LOG = logging.getLogger(__name__)
LOG.info(f"Setting up SERVICE - {__name__}")


def chunk_all_documents(raw_bible: List[RawDocument], version: str) -> List[BaseNode]:
    """Chunk all documents into nodes."""
    LOG.info(f"Chunking {len(raw_bible)} pages for Bible version: {version}")
    bible_nodes: List[TextNode] = []
    for raw_page in raw_bible:
        page_identifier: str = f"{raw_page.metadata['book']}-{raw_page.metadata['chapter']}-{raw_page.doc_id}-{version}"
        node: TextNode = TextNode(
            node_id=page_identifier,
            text=raw_page.doc_data,
            metadata=raw_page.metadata
        )
        bible_nodes.append(node)

    LOG.info(f"Chunking completed for Bible version: {version}, total nodes created: {len(bible_nodes)}")
    return bible_nodes