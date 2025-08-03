import logging
from typing import Dict, List
from flask import Blueprint, request
from src.models import BibleResponse, Prompt, PromptEnum
from src.service.prompting_service import store_prompts, get_prompts

LOG = logging.getLogger(__name__)
LOG.info(f"Setting up ROUTES - {__name__}")


prompting = Blueprint('prompting', __name__)


@prompting.route('/prompting/addContextPrompts', methods=['POST'])
def add_context() -> BibleResponse:
    try:
        store_prompts(prompts=Prompt.from_request(request=request))
        return BibleResponse.success(
            status="SUCCESS",
            message="Succesfully stored promtps"
        )
    except Exception as e:
        LOG.error(f"Unable to store prompts. Error: {e}")
        return BibleResponse.failure(
            status="FAILURE",
            message="Unable to store prompts due to system error"
        )
    

@prompting.route('/prompting/getContextPrompts', methods=['GET'])
def get_context_prompts() -> BibleResponse:
    version: str = request.get_json()["version"]

    try:
        prompts: Dict[str, Dict] = get_prompts(version=version)

        return BibleResponse.success(
            status="SUCCESS",
            message=f"Successfully retrieved prompts for Bible version: {version}",
            data=prompts
        )
    except Exception as e:
        LOG.error(e, exc_info=True)
        return BibleResponse.failure(
            status="FAILURE",
            message=f"Unable to retrieve prompts for Bible version: {version}"
        )