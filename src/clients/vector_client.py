import logging
from typing import List
from opensearchpy import OpenSearch, RequestsHttpConnection
from llama_index.vector_stores.opensearch import OpensearchVectorClient, OpensearchVectorStore
from llama_index.core.schema import BaseNode
from src import config


LOG = logging.getLogger(__name__)
INDEX = config.env_config.BIBLE_VERSION
OPENSEAERCH_ENDPOINT = config.env_config.OS_ENDPOINT
OS_CREDS: List[str] = config.env_config.OS_CREDS


def initiate_opensearch_vector_client() -> OpensearchVectorClient:
    """
    Initialize the OpenSearch client with the provided configuration.
    """
    LOG.info("Initializing OpenSearch client")
    client: OpenSearch = OpenSearch(
        hosts=[{'host': OPENSEAERCH_ENDPOINT, 'port': 443}],
        http_auth=(OS_CREDS[0], OS_CREDS[1]),
        use_ssl=True,
        verify_certs=True,
        ssl_show_warn=False,
        timeout=60,               # ← total timeout per request
        max_retries=3,            # ← simple retry
        retry_on_timeout=True,    # ← try again if timed out
        connection_class=RequestsHttpConnection
    )

    return OpensearchVectorClient(os_client=client, dim=1536, index=INDEX, endpoint=OPENSEAERCH_ENDPOINT)


def get_opensearch_vector_store() -> OpensearchVectorStore:
    """
    Get an OpenSearch vector store instance for the specified index.
    """
    return OpensearchVectorStore(client=os_client)

os_client: OpensearchVectorClient = initiate_opensearch_vector_client()