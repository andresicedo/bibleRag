import logging 
from typing import Dict, Iterable, List
from src.models import Prompt
from src.clients.mongo_client import get_mongo_prompt_collection
from pymongo.collection import Collection


LOG = logging.getLogger(__name__)
LOG.info(f"Setting up SERVICE - {__name__}")


def store_prompts(prompts: List[Prompt]):
    if not prompts:
        raise ValueError("No prompts provided")
    
    collection: Collection = get_mongo_prompt_collection()

    for prompt in prompts:
        collection.update_one(
            {"version": prompt.version, "role": prompt.role},
            {"$set": {
                "value": prompt.value
            }},
            upsert=True
        )

    LOG.info(f"Insert/Updated {len(prompts)} prompts for Bible version: {prompt.version}")
    

def get_prompts(version: str) -> Dict[str, Dict]:
    results: Dict[str, Dict] = {}
    collection: Collection = get_mongo_prompt_collection()
    prompts = collection.find({
        "version": version
    })

    for stored_prompt_obj in prompts:
        results[stored_prompt_obj["role"]] = {
            "version": version,
            "role": stored_prompt_obj["role"],
            "value": stored_prompt_obj["value"]
        }
    return results


def get_user_query_prompt(system_context: str, question_context: str, query: str) -> str:
    user_prompt: str = f"SYSTEM_CONTEXT: {system_context}"
    user_prompt += f"\nQUESTION_CONTEXT(CHUNKS, SCRIPTURE): {question_context}"
    user_prompt += f"\nUSER_QUESTION: {query}"
    return user_prompt
