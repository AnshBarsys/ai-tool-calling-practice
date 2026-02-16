#code for efactoring the action card services


from typing import Any, Dict, List, Optional
import logging

from app.agents.spec import AGENTS, AgentName, Envelope
from app.models.models import ActionCard, ActionCardType, FlatRecipe, Recipe

logger = logging.getLogger(__name__)


class ActionCardService:

    def __init__(self, settings, device_info_service):
        self.settings = settings
        self.device_info_service = device_info_service

async def build_action_cards(
        self, envelope: Envelope[Any], metadata=None
    ) -> List[ActionCard]:
        agent_id = envelope.metadata.agent_id
        payload = envelope.data
        device_status: Optional[str] = None  # Initialize device_status
        action_cards: List[ActionCard] = []

        if agent_id in (AgentName.CHAT.value, AgentName.DEVICE.value):
            response_text: str = getattr(payload, "response", "")
            if response_text:
                ac_env = await AGENTS[AgentName.ACTION_CARD].run(response_text)
                action_cards = ac_env.output.data.action_cards

        elif agent_id == AgentName.RECIPE.value:
            # Get recipes from payload
            recipes: List[FlatRecipe] = getattr(payload, "recipes", [])

            # Generate chat action cards using ACTION_CARD agent
            names = ", ".join(r.name for r in recipes) or "these recipes"
            ac_prompt = f"Suggest helpful chat action cards for {names}."
            ac_env = await AGENTS[AgentName.ACTION_CARD].run(ac_prompt)
            action_cards = ac_env.output.data.action_cards

        elif agent_id == AgentName.SETUP_STATIONS.value:
            # Get recipes and station configuration from payload
            recipes: List[FlatRecipe] = getattr(payload, "recipes", [])
            station_config = getattr(payload, "station_configuration", None)

            # Build "Setup Stations" action card with configuration data
            if station_config:
                setup_card = ActionCard(
                    type=ActionCardType.DEVICE,
                    label="Setup Stations",
                    value="Setup my stations with these ingredients",
                    action_id="redirect:setup_stations",
                    data={
                        "station_configuration": self._safe_serialize(station_config)
                    },
                )
                action_cards.append(setup_card)

            # Generate chat action cards using ACTION_CARD agent
            names = ", ".join(r.name for r in recipes) or "station setup"
            ac_prompt = (
                f"Suggest helpful chat action cards for {names} station configuration."
            )
            ac_env = await AGENTS[AgentName.ACTION_CARD].run(ac_prompt)
            chat_cards = ac_env.output.data.action_cards

            # Filter out redirect:setup_barsys360 cards since we already have redirect:setup_stations
            # This prevents duplicate setup-related action cards
            chat_cards = [
                card
                for card in chat_cards
                if getattr(card, "action_id", None) != "redirect:setup_barsys360"
            ]

            action_cards.extend(chat_cards)

        if (
            metadata
            and metadata.device
            and hasattr(metadata.device, "connection_status")
        ):
            device_status = metadata.device.connection_status
        else:
            # Handle the case where metadata.device is None or lacks connection_status.
            # For now, let's assume 'disconnected' if no device info.
            device_status = "disconnected"

        if device_status == "disconnected":
            action_cards.append(
                ActionCard(
                    type=ActionCardType.DEVICE,
                    label="Connect Device",
                    value="Connect barsys device",
                    action_id="redirect:connect_device",
                    data={},
                )
            )
        # if no device metadata or device number is empty, add a shop action card
        if not metadata or (
            not metadata.device or not getattr(metadata.device, "device_number", None)
        ):
            action_cards.append(
                ActionCard(
                    type=ActionCardType.SHOP,
                    label="Barsys Shop",
                    value="I want to check out the Barsys shop",
                    action_id="redirect:shop",
                    data={
                        "shop_label": "Barsys Shop",
                        "shop_url": self.settings.shop_url,
                    },
                )
            )
        return action_cards

async def populate_device_action_card_data(
        self,
        action_cards: List[ActionCard],
        device_context: Optional[Dict[str, Any]],
    ) -> None:
        """
        Populate data for device action cards based on device context.
        This centralizes the action card data population logic.
        """
        if not device_context:
            return

        for ac in action_cards:
            if getattr(ac, "type", None) == ActionCardType.DEVICE:
                if getattr(ac, "action_id", None) == "redirect:clean_device":
                    # Get stations with some quantity for clean device action
                    stations = await self._get_stations_with_quantity(device_context)
                    ac.data = {"stations": stations}
                # Note: Other device action cards (e.g., redirect:connect_device, redirect:setup_stations)
                # already have their data populated when created, so no additional handling needed here

def get_fallback_action_cards(
        self, intent: str, recipes: List[Recipe]
    ) -> List[ActionCard]:
        """Generate fallback action cards when the agent fails to generate them."""
        from app.models.models import ActionCard, ActionCardType

        fallback_cards = []

        # Add craft cards for recipes
        for recipe in recipes:
            fallback_cards.append(
                ActionCard(
                    type=ActionCardType.CRAFT,
                    label=f"Craft a {recipe.name}",
                    value=f"Craft me a {recipe.name}",
                    action_id=f"craft_{recipe.name.lower().replace(' ', '_')}",
                    data={"recipe": recipe.model_dump(exclude_none=True)},
                )
            )

        # Add generic chat cards based on intent
        if intent == "recipe":
            fallback_cards.extend(
                [
                    ActionCard(
                        type=ActionCardType.CHAT,
                        label="Similar Cocktails",
                        value="What are similar cocktails?",
                        action_id="similar_cocktails",
                        data={},
                    ),
                    ActionCard(
                        type=ActionCardType.CHAT,
                        label="Cocktail Tips",
                        value="What are some cocktail making tips?",
                        action_id="cocktail_tips",
                        data={},
                    ),
                ]
            )
        elif intent == "device":
            fallback_cards.extend(
                [
                    ActionCard(
                        type=ActionCardType.CHAT,
                        label="Contact Support",
                        value="How do I contact Barsys support?",
                        action_id="contact_support",
                        data={},
                    ),
                    ActionCard(
                        type=ActionCardType.CHAT,
                        label="Device Setup",
                        value="How do I set up my Barsys device?",
                        action_id="device_setup",
                        data={},
                    ),
                ]
            )
        else:  # chat or off_topic
            fallback_cards.extend(
                [
                    ActionCard(
                        type=ActionCardType.CHAT,
                        label="Popular Cocktails",
                        value="What are the most popular cocktails?",
                        action_id="popular_cocktails",
                        data={},
                    ),
                    ActionCard(
                        type=ActionCardType.CHAT,
                        label="Barsys Help",
                        value="I need help with my Barsys device",
                        action_id="device_help",
                        data={},
                    ),
                    ActionCard(
                        type=ActionCardType.CHAT,
                        label="New Recipe",
                        value="Suggest a new cocktail recipe",
                        action_id="new_recipe",
                        data={},
                    ),
                ]
            )

        # Ensure we have exactly 2-5 cards
        return fallback_cards[:5] if len(fallback_cards) > 5 else fallback_cards

def get_device_context_for_faq(self, user_message: str, top_k: int = 3) -> str:
        """
        Retrieve relevant device documentation chunks for the user's query using DeviceInfoService.
        """
        try:
            results = self.device_info_service.search_faq(user_message, top_k=top_k)
            if not results:
                logger.info("No relevant device documentation found for query")
                return ""
            context_parts = []
            for i, (text, source, index) in enumerate(results, 1):
                context_parts.append(
                    f"Documentation Chunk {i} (Source: {source}):\n{text}"
                )
            device_context = "\n\n".join(context_parts)
            logger.info(
                f"Retrieved {len(results)} device documentation chunks for context"
            )
            return f"\n\n<device_documentation_context>\n{device_context}\n</device_documentation_context>\n"
        except Exception as e:
            logger.error(f"Error retrieving device context: {e}")
            return ""
