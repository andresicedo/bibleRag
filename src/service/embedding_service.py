import logging
import concurrent.futures
from typing import List
from time import sleep
from llama_index.core.schema import BaseNode
from llama_index.vector_stores.opensearch import OpensearchVectorStore
from openai.types import CreateEmbeddingResponse
from src.clients.llm_client import get_text_embedding
from src.clients.vector_client import get_opensearch_vector_store


LOG = logging.getLogger(__name__)
LOG.info(f"Setting up SERVICE - {__name__}")

def embed_bible_nodes(processed_bible_nodes: List[BaseNode], version: str):
    """Embed Bible nodes for the specified version."""
    LOG.info(f"Embedding {len(processed_bible_nodes)} nodes for Bible version: {version}")
    
    def embed_node(node: BaseNode):
        try:
            embedding_response: CreateEmbeddingResponse = get_text_embedding(
                text=node.get_content()
            )
            node.embedding = embedding_response.data[0].embedding
        except Exception as e:
            LOG.error(f"Error embedding node {node.node_id}: {str(e)}")
            raise RuntimeError(f"Failed to embed node {node.node_id}: {str(e)}")
        
    try:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=15)
        futures = [executor.submit(embed_node, node) for node in processed_bible_nodes]
        for future in concurrent.futures.as_completed(futures):
            future.result()
        LOG.info(f"Embedding completed for Bible version: {version}")
    except Exception as e:
        LOG.error(f"Error during embedding process for Bible version {version}: {str(e)}")
        raise RuntimeError(f"Failed to embed Bible nodes for version {version}: {str(e)}")
    

def store_embedded_bible_nodes_in_vector_db(processed_bible_nodes: List[BaseNode], version: str):
    """Store embedded Bible nodes in a vector database."""
    LOG.info(f"Storing {len(processed_bible_nodes)} embedded nodes for Bible version: {version}")
    vector_store: OpensearchVectorStore = get_opensearch_vector_store()
    node_ids = [node.node_id for node in processed_bible_nodes]

    try:
        vector_store.delete_nodes(node_ids=node_ids)
        LOG.info(f"Deleted existing nodes for Bible version: {version}")

        batch_size = 100
        for i in range(0, len(processed_bible_nodes), batch_size):
            batch = processed_bible_nodes[i:i+batch_size]
            try:
                vector_store.add(nodes=batch)
                LOG.info(f"Stored batch {i // batch_size + 1} ({len(batch)} nodes)")
            except Exception as e:
                LOG.error(f"Error storing batch {i // batch_size + 1}: {str(e)}")
                sleep(2)  # gentle retry delay
        LOG.info(f"Stored {len(processed_bible_nodes)} embedded nodes for Bible version: {version}")
    except Exception as e:
        LOG.error(f"Error storing embedded nodes for Bible version {version}: {str(e)}")
        raise e
