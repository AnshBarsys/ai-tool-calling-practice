to test the changes made in handling chat requests:

import asyncio
from app.services.chat_service import ChatService
from app.models.service_models import ChatRequest, ImageInput
from app.services.memory_service import MemoryService
from app.services.vision_service import VisionService
from app.services.intent_service import IntentService
from app.services.recipe_publishing_service import RecipePublishingService
from app.services.action_card_service import ActionCardService
from app.services.barsys_content_search_service import BarsysContentSearchService
from app.services.website_search_service import WebsiteSearchService
from app.services.device_service import DeviceService
from app.services.device_info_service import DeviceInfoService
from app.services.ingredient_service import IngredientService
from app.services.conversation_service import ConversationService
from app.core.config import Settings

# --- Minimal mocks ---
memory_service = MemoryService()
vision_service = VisionService()
intent_service = IntentService()
recipe_service = RecipePublishingService()
barsys_service = BarsysContentSearchService()
website_service = WebsiteSearchService()
device_service = DeviceService()
device_info_service = DeviceInfoService()
ingredient_service = IngredientService()
conversation_service = ConversationService()
settings = Settings()

chat_service = ChatService(
    vision_service=vision_service,
    memory_service=memory_service,
    intent_service=intent_service,
    recipe_publishing_service=recipe_service,
    barsys_content_search_service=barsys_service,
    website_search_service=website_service,
    device_info_service=device_info_service,
    device_service=device_service,
    ingredient_service=ingredient_service,
    conversation_service=conversation_service,
    settings=settings,
)


async def main():
    request = ChatRequest(
        session_id="test_session",
        user_id="user_1",
        input=ImageInput(url=None),  # text only for now
    )
    response = await chat_service.handle_chat_request(request)
    print("Chat Response:", response)


asyncio.run(main())
