import logging
import concurrent.futures
import uuid
from flask import Blueprint, request
from typing import List
from llama_index.core.schema import BaseNode, TextNode
from llama_index.core.vector_stores.types import VectorStoreQueryResult
from src.models import RawDocument, BibleRequest, BibleResponse
from src.service.document_service import process_documents, store_bible_nodes_in_document_db
from src.service.indexing_service import chunk_all_documents
from src.service.postprocessing_service import identify_ceiling_exceeding_nodes, chunk_ceiling_exceeding_nodes
from src.service.embedding_service import embed_bible_nodes, store_embedded_bible_nodes_in_vector_db
from src.service.retrieval_service import retrieve_top_k_query_results, generate_response_from_chunks

LOG = logging.getLogger(__name__)
LOG.info(f"Setting up ROUTES - {__name__}")

rag = Blueprint('rag', __name__)
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


@rag.route('initiate', methods=['POST'])
def initiate_rag() -> BibleResponse:
    """Initiate a RAG process with the provided documents."""
    bible_request: BibleRequest = BibleRequest.from_request(request=request, qna=False)

    try:
        LOG.info("preprocessing stage for Bible version: %s STARTED", bible_request.version)
        raw_bible: List[RawDocument] = process_documents(bible_request=bible_request)
        LOG.info("Preprocessing stage for Bible version: %s COMPLETED", bible_request.version)

        LOG.info("Indexing stage for Bible version: %s STARTED", bible_request.version)
        chunked_bible_nodes: List[TextNode] = chunk_all_documents(raw_bible=raw_bible, version=bible_request.version)

        LOG.info("Postprocessing stage for Bible version: %s STARTED", bible_request.version)
        ceiling_exceeding_nodes, chunked_bible_nodes = identify_ceiling_exceeding_nodes(nodes=chunked_bible_nodes, version=bible_request.version)

        if ceiling_exceeding_nodes:
            LOG.info("Postprocessing stage: Chunking token ceiling exceeding nodes for Bible version: %s", bible_request.version)
            truncated_nodes: List[BaseNode] = chunk_ceiling_exceeding_nodes(nodes=ceiling_exceeding_nodes, version=bible_request.version)
            chunked_bible_nodes.extend(truncated_nodes)
        LOG.info("Postprocessing stage: Chunking COMPLETED for Bible version: %s", bible_request.version)  

        LOG.info("Embedding stage for Bible version: %s STARTED", bible_request.version)
        embed_bible_nodes(processed_bible_nodes=chunked_bible_nodes, version=bible_request.version)
        LOG.info("Embedding stage for Bible version: %s COMPLETED", bible_request.version)
        LOG.info("Indexing stage for Bible version: %s COMPLETED", bible_request.version)

        LOG.info("Storing stage for Bible version: %s STARTED", bible_request.version)
        with executor:
            futures = [
                executor.submit(store_embedded_bible_nodes_in_vector_db, processed_bible_nodes=chunked_bible_nodes, version=bible_request.version),
                executor.submit(store_bible_nodes_in_document_db, processed_bible_nodes=chunked_bible_nodes, version=bible_request.version)
            ]
            concurrent.futures.wait(futures)
        LOG.info("Storing stage for Bible version: %s COMPLETED", bible_request.version)
        
        return BibleResponse.success(status="SUCCESS", message="RAG process initiated sucessfully", data={"version": bible_request.version})
    except Exception as e:
        LOG.error("Error initiating RAG: %s", str(e))
        return BibleResponse.failure("error", "Failed to initiate RAG process")


@rag.route('/query', methods=['POST'])
def query_rag() -> BibleResponse:
    """Query the RAG system with a Bible request."""
    try:
        bible_request = BibleRequest.from_request(request=request, qna=True)
        LOG.info("Processing RAG query for version: %s", bible_request.version)
        
        if bible_request.session_id is None:
            bible_request.session_id = str(uuid.uuid4())

        top_k_results: VectorStoreQueryResult = retrieve_top_k_query_results(bible_request=bible_request)
        if not top_k_results:
            return BibleResponse.not_found(
                status="FAILED",
                message=f"No relevant scripture found for {bible_request.query}"
            )
        LOG.info(f"Retrieval stage for bible version: {bible_request.version} COMPLETED")

        response_text: str = generate_response_from_chunks(
            bible_request=bible_request, chunks=top_k_results.nodes
        )

        if not response_text:
            return BibleResponse.failure(
                status="FAILURE",
                message=f"Failed to retrieve a response for the question: {bible_request.query}"
            )
        
        return BibleResponse.success(
            status="SUCCESS", 
            message="RAG query processed", 
            data=response_text, 
            session_id=bible_request.session_id)
    except Exception as e:
        LOG.error("Error processing RAG query: %s", str(e))
        return BibleResponse.failure("error", "Failed to process Bible query")