#refactoring "_identify_intent" from chatservice to new dedicated file
#new file created - intent_service.py


import logging
from typing import List

from pydantic_ai.messages import ModelMessage
from app.agents.spec import AGENTS, AgentName
from app.services.memory_service import MemoryService
from app.core.logtools import log_execution_time

logger = logging.getLogger(__name__)


class IntentService:
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service

    async def identify(
        self,
        user_message: str,
        history: List[ModelMessage],
    ) -> AgentName:

        intent_history = await self.memory_service.prepend(
            history.copy(), AgentName.INTENT.value
        )

        with log_execution_time("Identifying intent"):
            run_result = await AGENTS[AgentName.INTENT].run(
                user_message,
                message_history=intent_history,
            )

            intent = run_result.output.data.intent.lower()

            if intent == "looking_for_recipe":
                return AgentName.RECIPE

            try:
                return AgentName(intent)
            except ValueError:
                logger.warning(f"Unknown intent: {intent}")
                raise


#result- working!
