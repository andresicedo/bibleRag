import logging
from typing import Dict, Iterable, List, Optional
from llama_index.vector_stores.opensearch import OpensearchVectorStore
from llama_index.core.vector_stores.types import (
    MetadataFilter, MetadataFilters, FilterCondition, FilterOperator, 
    VectorStoreQuery, VectorStoreQueryResult
)
from llama_index.core.schema import BaseNode
from llama_index.core.llms import ChatMessage, MessageRole
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from src.models import BibleRequest, BibleReference
from src.clients.vector_client import get_opensearch_vector_store
from src.clients.llm_client import get_chat_response
from src.service.embedding_service import get_text_embedding
from src.service.chat_service import get_chat_history, update_chat_history, map_chat_messages
from src.service.prompting_service import get_prompts, get_user_query_prompt


LOG = logging.getLogger(__name__)
LOG.info(f"Settup up SERVICE - {__name__}")


def retrieve_top_k_query_results(bible_request: BibleRequest) -> VectorStoreQueryResult:
    if not bible_request.query and not bible_request.version:
        raise ValueError("Query and version must be provided.")
    
    # embed the query
    query_embedding = get_text_embedding(text=bible_request.query).data[0].embedding

    # get the opensearch vector store
    os_vector_store: OpensearchVectorStore = get_opensearch_vector_store()

    max_top_k: int = 20 # can be logic based in future enhancement

    # perform the search
    vector_store_query: VectorStoreQuery = VectorStoreQuery(
        query_embedding=query_embedding, similarity_top_k=max_top_k, filters=get_open_search_metadata_filters(bible_references=bible_request.bible_references)
    )

    return os_vector_store.query(vector_store_query)


def get_open_search_metadata_filters(bible_references: List[BibleReference]) -> MetadataFilters:
    if not bible_references:
        raise ValueError("Bible references must be provided.")

    filters = [
        MetadataFilter(
            key="book",
            value=bible_reference.book,
            operator=FilterOperator.EQ
        )
        for bible_reference in bible_references
    ]

    if len(filters) > 1:
        return MetadataFilters(filters=filters, condition=FilterCondition.OR)
    
    return MetadataFilters(filters=filters)


def generate_response_from_chunks(bible_request: BibleRequest, chunks: List[BaseNode]) -> str:
    prompts: Dict[str, Dict] = get_prompts(version=bible_request.version)
    role_context: str = prompts.get("ROLE_PROMPT", None)["value"] if prompts else None
    system_context: str = prompts.get("SYSTEM_PROMPT", None)["value"] if prompts else None
    query_context = "/n---/n".join([chunk.get_content() for chunk in chunks])

    chat_messages: List[ChatMessage] = []
    chat_history: List[ChatMessage] = get_chat_history(session_id=bible_request.session_id)

    user_prompt: str = get_user_query_prompt(
        system_context=system_context,
        question_context=query_context,
        query=bible_request.query
    )

    chat_messages.append(ChatMessage(role=MessageRole.SYSTEM, content=role_context))
    if chat_history and len(chat_history) > 0:
        chat_messages.extend(chat_history)
    chat_messages.append(ChatMessage(role=MessageRole.USER, content=user_prompt))
    chat_messages_param: Iterable[ChatCompletionMessageParam] = map_chat_messages(chat_messages=chat_messages)
    
    response: ChatCompletion = get_chat_response(chat_messages=chat_messages_param)
    content: str = response.choices[0].message.content

    latest_query_and_response: List[ChatMessage] = [
        ChatMessage(role=MessageRole.USER, content=bible_request.query),
        ChatMessage(role=MessageRole.USER, content=content)]
    
    update_chat_history(session_id=bible_request.session_id, chat_messages=latest_query_and_response)

    return content

