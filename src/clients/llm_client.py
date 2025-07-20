import logging
from typing import Iterable, List
from openai import OpenAI
from openai.types import chat, CreateEmbeddingResponse
from src import config

LOG = logging.getLogger(__name__)
response_model: str = config.env_config.OPEN_AI_MODEL
embedding_model: str = config.env_config.OPEN_AI_EMBEDDING_MODEL


def initialize_openai_client() -> OpenAI:
    """Initialize the OpenAI client with the provided API key."""
    api_key: str = config.env_config.OPEN_AI_API_KEY
    return OpenAI(api_key=api_key)


def get_text_embedding(text: str, metadata_context: str) -> CreateEmbeddingResponse:
    """Get embedding for the provided text using the OpenAI client.
        Response: CreateEmbeddingResponse with the List[float] embedding data located at response.data[0].embedding.
    """
    LOG.info("Getting embeddings for document details: %s", metadata_context)

    response: CreateEmbeddingResponse = client.embeddings.create(
        model=embedding_model,
        input=text
    )
    return response


def get_chat_response(chat_messages: Iterable[chat.ChatCompletionMessageParam], max_tokens: int = 2000) -> chat.ChatCompletion:
    """Get chat response from OpenAI using the provided messages."""
    return client.chat.completions.create(
        model=response_model,
        messages=chat_messages,
        max_tokens=max_tokens
    )


client: OpenAI = initialize_openai_client()