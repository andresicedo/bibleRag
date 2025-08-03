import logging
from typing import Iterable, List
from llama_index.core.llms import ChatMessage, MessageRole
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam
)
from llama_index.storage.chat_store.mongo import MongoChatStore
from src.clients.mongo_client import get_mongo_chat_store

LOG = logging.getLogger(__name__)
LOG.info(f"Setting up service - {__name__}")


def get_chat_history(session_id: str) -> List[ChatMessage]:
    mongo_chat_store: MongoChatStore = get_mongo_chat_store()
    return mongo_chat_store.get_messages(key=session_id)


def update_chat_history(session_id: str, chat_messages: List[ChatMessage]):
    mongo_chat_store: MongoChatStore = get_mongo_chat_store()
    for chat_message in chat_messages:
        mongo_chat_store.add_message(key=session_id, message=chat_message)


def clear_chat_history(session_id: str):
    mongo_chat_store: MongoChatStore = get_mongo_chat_store()
    return mongo_chat_store.delete_messages(key=session_id)


def map_chat_messages(chat_messages: List[ChatMessage]) -> Iterable[ChatCompletionMessageParam]:
    message_params: List[ChatCompletionMessageParam] = []
    for message in chat_messages:
        if message.role == MessageRole.SYSTEM:
            message_params.append(ChatCompletionSystemMessageParam(role=message.role, content=message.content))
        elif message.role == MessageRole.USER:
            message_params.append(ChatCompletionUserMessageParam(role=message.role, content=message.content))
        else:
            raise ValueError(f"Unknown role: {message.role}")
    return message_params
