# TODO create a postprocessing service to handle token ceiling exceeding nodes and tagging nodes with metadata
import logging
from typing import List, Dict
from llama_index.core.schema import BaseNode, TextNode

LOG = logging.getLogger(__name__)


def identify_ceiling_exceeding_nodes(nodes: List[BaseNode], version: str) -> List[BaseNode]:
    return []

def chunk_ceiling_exceeding_nodes(nodes: List[BaseNode], version: str) -> List[BaseNode]:
    """Chunk nodes that exceed the token ceiling into smaller nodes."""
    return []

    
    