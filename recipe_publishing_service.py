import logging
import httpx
from typing import List

from app.models.models import Recipe
from app.models.service_models import ChatRequest
from app.core.config import Settings

logger = logging.getLogger(__name__)


class RecipePublishingService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def publish_flat_recipes(
        self,
        recipes: List[Recipe],
        request: ChatRequest,
    ) -> None:
        """
        Publishes AI-generated flat recipes to the external Defteros API
        and enriches them with UUIDs returned from the service.
        """

        if not recipes:
            return

        flat_recipe_url = (
            f"{self.settings.defteros_api_url.rstrip('/')}/recipes/flat"
        )

        try:
            user_id = getattr(request, "user_id", None)
            headers = {"X-User-Id": str(user_id)} if user_id else {}

            for recipe in recipes:
                flat_recipe_json = recipe.model_dump(
                    mode="json",
                    exclude_none=True,
                )

                recipe_payload = {
                    "name": recipe.name,
                    "session_id": request.session_id,
                    "flat_recipe_content": flat_recipe_json,
                }

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        flat_recipe_url,
                        json=recipe_payload,
                        headers=headers,
                        timeout=30.0,
                    )
                    response.raise_for_status()

                    result = response.json()
                    recipe_uuid = result.get("uuid") or result.get("id")

                    recipe.full_recipe_id = recipe_uuid

                    logger.info(
                        f"Successfully published recipe '{recipe.name}' "
                        f"UUID={recipe_uuid}"
                    )

        except httpx.HTTPError:
            logger.exception("HTTP error while publishing flat recipes")

        except Exception:
            logger.exception("Unexpected error while publishing flat recipes")
