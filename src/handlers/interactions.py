"""
Handlers for Slack interactive components (buttons, modals, etc.)
"""

from collections.abc import Awaitable, Callable
from json import loads
from typing import Any

from loguru import logger
from slack_sdk.web.async_client import AsyncWebClient

from src.commands.command_factory import CommandFactory
from src.controllers.lobby_details import get_lobby_details
from src.models.db import Game


async def handle_refresh_game_status(ack: Callable[[], Awaitable[None]], body: dict[str, Any], say: Callable) -> None:
    """
    Handle the refresh game status button click.
    Re-fetches game status from the web and posts an updated message.
    """
    await ack()

    game_name = body["actions"][0]["value"]
    logger.info(f"Refreshing game status for: {game_name}")

    try:
        game_details = await get_lobby_details(game_name, use_db=False)

        if game_details:
            await say({"blocks": game_details, "text": f"Refreshed status for {game_name}"})
        else:
            await say({"text": f"❌ Failed to refresh status for game '{game_name}'"})

    except Exception as e:
        logger.error(f"Error refreshing game status: {e}")
        await say({"text": f"❌ Error refreshing game status: {e!s}"})


async def handle_set_primary_game(ack: Callable[[], Awaitable[None]], body: dict[str, Any], say: Callable) -> None:
    """
    Handle the set primary game button click.
    Sets the clicked game as the primary game.
    """
    await ack()

    game_name = body["actions"][0]["value"]
    logger.info(f"Setting primary game to: {game_name}")

    try:
        # Use the existing command to set primary game
        command_obj = CommandFactory.get_command("game primary")
        response = await command_obj.execute(game_name)

        # The response is already JSON formatted from the command
        import json

        response_blocks = json.loads(response)
        await say({"blocks": response_blocks, "text": f"Primary game set to {game_name}"})

    except Exception as e:
        logger.error(f"Error setting primary game: {e}")
        await say({"text": f"❌ Error setting primary game: {e!s}"})


async def open_remove_game_modal(ack: Callable[[], Awaitable[None]], body: dict[str, Any], client: AsyncWebClient) -> None:
    """
    Open a modal with a dropdown to select a game to remove.
    """
    await ack()

    try:
        # Fetch active games from database
        games = await Game.filter(active=True).all()

        if not games:
            # No games to remove
            await client.chat_postEphemeral(
                channel=body["channel"]["id"],
                user=body["user"]["id"],
                text="ℹ️ No active games found. Use `/dom game add [game_name]` to track a game.",
            )
            return

        # Build options for the select menu
        options = [
            {
                "text": {"type": "plain_text", "text": game.nickname or game.name},
                "value": game.name,
            }
            for game in games
        ]

        # Open the modal
        await client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "remove_game_modal_submit",
                "title": {"type": "plain_text", "text": "Remove Game"},
                "submit": {"type": "plain_text", "text": "Remove"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "game_selection",
                        "element": {
                            "type": "static_select",
                            "action_id": "selected_game",
                            "placeholder": {"type": "plain_text", "text": "Select a game to remove"},
                            "options": options,
                        },
                        "label": {"type": "plain_text", "text": "Game to remove"},
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "⚠️ *Warning*\nThis will deactivate the game and stop tracking updates. The game data will remain in the database but will be marked as inactive.",
                        },
                    },
                ],
            },
        )

    except Exception as e:
        logger.error(f"Error opening remove game modal: {e}")


async def handle_remove_game_modal_submit(ack: Callable[[], Awaitable[None]], body: dict[str, Any], client: AsyncWebClient) -> None:
    """
    Handle the submission of the remove game modal.
    """
    await ack()

    try:
        # Extract the selected game name from the modal submission
        values = body["view"]["state"]["values"]
        game_name = values["game_selection"]["selected_game"]["selected_option"]["value"]

        logger.info(f"Removing game: {game_name}")

        # Use the existing command to remove the game
        command_obj = CommandFactory.get_command("game remove")
        response = await command_obj.execute(game_name)

        # Parse the response and send it to the channel
        response_blocks = loads(response)

        # Post message to the channel where the modal was triggered
        await client.chat_postMessage(
            channel=body["user"]["id"],  # Send as DM
            blocks=response_blocks,
            text=f"Game {game_name} removed",
        )

    except Exception as e:
        logger.error(f"Error handling remove game modal submit: {e}")


async def open_set_primary_modal(ack: Callable[[], Awaitable[None]], body: dict[str, Any], client: AsyncWebClient) -> None:
    """
    Open a modal with a dropdown to select a game to set as primary.
    """
    await ack()

    try:
        # Fetch active games from database
        games = await Game.filter(active=True).all()

        if not games:
            await client.chat_postEphemeral(
                channel=body["channel"]["id"],
                user=body["user"]["id"],
                text="ℹ️ No active games found. Use `/dom game add [game_name]` to track a game.",
            )
            return

        # Build options for the select menu
        options = []
        for game in games:
            display_name = game.nickname or game.name
            if game.primary_game:
                display_name += " ⭐ (currently primary)"
            options.append(
                {
                    "text": {"type": "plain_text", "text": display_name},
                    "value": game.name,
                }
            )

        # Open the modal
        await client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "set_primary_modal_submit",
                "title": {"type": "plain_text", "text": "Set Primary Game"},
                "submit": {"type": "plain_text", "text": "Set Primary"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "game_selection",
                        "element": {
                            "type": "static_select",
                            "action_id": "selected_game",
                            "placeholder": {"type": "plain_text", "text": "Select primary game"},
                            "options": options,
                        },
                        "label": {"type": "plain_text", "text": "Primary Game"},
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "ℹ️ The primary game is used by `/dom turn` to quickly check status without specifying a game name.",
                        },
                    },
                ],
            },
        )

    except Exception as e:
        logger.error(f"Error opening set primary modal: {e}")


async def handle_set_primary_modal_submit(ack: Callable[[], Awaitable[None]], body: dict[str, Any], client: AsyncWebClient) -> None:
    """
    Handle the submission of the set primary game modal.
    """
    await ack()

    try:
        # Extract the selected game name from the modal submission
        values = body["view"]["state"]["values"]
        game_name = values["game_selection"]["selected_game"]["selected_option"]["value"]

        logger.info(f"Setting primary game to: {game_name}")

        # Use the existing command to set primary game
        command_obj = CommandFactory.get_command("game primary")
        response = await command_obj.execute(game_name)

        # Parse the response and send it to the user
        response_blocks = loads(response)

        await client.chat_postMessage(
            channel=body["user"]["id"],  # Send as DM
            blocks=response_blocks,
            text=f"Primary game set to {game_name}",
        )

    except Exception as e:
        logger.error(f"Error handling set primary modal submit: {e}")


async def open_add_game_modal(ack: Callable[[], Awaitable[None]], body: dict[str, Any], client: AsyncWebClient) -> None:
    """
    Open a modal with a form to add a new game.
    """
    await ack()

    try:
        await client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "add_game_modal_submit",
                "title": {"type": "plain_text", "text": "Add New Game"},
                "submit": {"type": "plain_text", "text": "Add Game"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "game_name_input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "game_name",
                            "placeholder": {"type": "plain_text", "text": "Enter game name (e.g., MyGame)"},
                        },
                        "label": {"type": "plain_text", "text": "Game Name"},
                        "hint": {
                            "type": "plain_text",
                            "text": "Must match the exact game name on the Dominions server",
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "nickname_input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "nickname",
                            "placeholder": {"type": "plain_text", "text": "Optional display name"},
                        },
                        "label": {"type": "plain_text", "text": "Nickname (Optional)"},
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "set_primary_input",
                        "element": {
                            "type": "checkboxes",
                            "action_id": "set_primary",
                            "options": [
                                {
                                    "text": {"type": "plain_text", "text": "Set as primary game"},
                                    "value": "set_primary",
                                }
                            ],
                        },
                        "label": {"type": "plain_text", "text": "Options"},
                        "optional": True,
                    },
                ],
            },
        )

    except Exception as e:
        logger.error(f"Error opening add game modal: {e}")


async def handle_add_game_modal_submit(ack: Callable[[], Awaitable[None]], body: dict[str, Any], client: AsyncWebClient) -> None:
    """
    Handle the submission of the add game modal.
    """
    await ack()

    try:
        # Extract values from the modal submission
        values = body["view"]["state"]["values"]
        game_name = values["game_name_input"]["game_name"]["value"]
        nickname = values["nickname_input"]["nickname"]["value"]
        set_primary_checked = values["set_primary_input"]["set_primary"].get("selected_options", [])

        logger.info(f"Adding game: {game_name}, nickname: {nickname}, set_primary: {bool(set_primary_checked)}")

        # Use the existing command to add the game
        command_obj = CommandFactory.get_command("game add")
        response = await command_obj.execute(game_name)

        # Parse the response
        response_blocks = loads(response)

        # If nickname was provided, set it
        if nickname:
            nickname_cmd = CommandFactory.get_command("game nickname")
            await nickname_cmd.execute(game_name, nickname)

        # If set_primary was checked, set it as primary
        if set_primary_checked:
            primary_cmd = CommandFactory.get_command("game primary")
            await primary_cmd.execute(game_name)

        # Send success message
        await client.chat_postMessage(
            channel=body["user"]["id"],  # Send as DM
            blocks=response_blocks,
            text=f"Game {game_name} added successfully",
        )

    except Exception as e:
        logger.error(f"Error handling add game modal submit: {e}")
        # Send error message to user
        try:
            await client.chat_postMessage(
                channel=body["user"]["id"],
                text=f"❌ Error adding game: {e!s}",
            )
        except Exception:
            pass
