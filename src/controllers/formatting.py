from typing import Any

from src.models.app.lobby_details import LobbyDetails


def create_success_block(message: str, details: str | None = None) -> list[dict[str, Any]]:
    """
    Create a success message block with optional details.

    :param message: Main success message
    :param details: Optional additional details
    :return: List of Slack blocks for success message
    """
    blocks: list[dict[str, Any]] = [
        {"type": "section", "text": {"type": "mrkdwn", "text": f":white_check_mark: *{message}*"}},
    ]

    if details:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": details}})

    return blocks


def create_error_block(message: str, suggestion: str | None = None) -> list[dict[str, Any]]:
    """
    Create an error message block with optional suggestion.

    :param message: Error message
    :param suggestion: Optional suggestion to fix the error
    :return: List of Slack blocks for error message
    """
    blocks: list[dict[str, Any]] = [
        {"type": "section", "text": {"type": "mrkdwn", "text": f":x: *Error*\n{message}"}},
    ]

    if suggestion:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f"💡 *Suggestion*\n{suggestion}"}})

    return blocks


def create_info_block(message: str, details: str | None = None) -> list[dict[str, Any]]:
    """
    Create an info message block with optional details.

    :param message: Info message
    :param details: Optional additional details
    :return: List of Slack blocks for info message
    """
    blocks: list[dict[str, Any]] = [
        {"type": "section", "text": {"type": "mrkdwn", "text": f":information_source: *{message}*"}},
    ]

    if details:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": details}})

    return blocks


def create_warning_block(message: str, details: str | None = None) -> list[dict[str, Any]]:
    """
    Create a warning message block with optional details.

    :param message: Warning message
    :param details: Optional additional details
    :return: List of Slack blocks for warning message
    """
    blocks: list[dict[str, Any]] = [
        {"type": "section", "text": {"type": "mrkdwn", "text": f":warning: *{message}*"}},
    ]

    if details:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": details}})

    return blocks


def get_emoji(turn_status: str) -> str:
    """
    This function takes a player's turn status as an argument and returns an emoji that corresponds to the status.
    The function uses Python's match statement to check the value of turn_status and return the appropriate emoji.

    :param turn_status: A string representing the player's turn status. Expected values include "Turn played" or "-".
    :return: A string representing an emoji.
    """
    match turn_status:
        case "Turn played":
            return ":white_check_mark:"
        case "Turn unfinished":
            return ":question:"
        case "Eliminated":
            return ":dom_rip:"
        case "-":
            return ":x:"
        case _:
            return ":gungoose:"


def create_nations_block(player_list: list) -> list:
    """
    Attempts to create and format a slack modal

    :param player_list:
    :return:
    """
    player_blocks = []

    for player in player_list:
        player.turn_emoji = get_emoji(player.turn_status)

        nation_section = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{player.turn_emoji} - *{player.name.strip()}*"},
        }

        player_blocks.append(nation_section)
    return player_blocks


def create_game_details_block(lobby_details: LobbyDetails, game_name: str | None = None) -> list[Any]:
    """
    Attempt to format general lobby details from web (LIVE data)

    :param lobby_details: Game lobby details
    :param game_name: Name of the game (for action buttons)
    :return: List of Slack blocks
    """
    formatted_msg = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Dominions Times"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " :freak_lord: *Update* :freak_lord: 🔴 *LIVE*",
            },
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": "🔴 Real-time data from Dominions server"}],
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{lobby_details.server_info}"},
        },
        {"type": "divider"},
    ]

    # Add action buttons if game_name is provided
    if game_name:
        formatted_msg.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🔄 Refresh"},
                        "value": game_name,
                        "action_id": "refresh_game_status",
                        "style": "primary",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "⭐ Set Primary"},
                        "value": game_name,
                        "action_id": "set_primary_game",
                    },
                ],
            }
        )

    formatted_msg.append({"type": "section", "text": {"type": "mrkdwn", "text": "*Player List*"}})
    return formatted_msg


def create_game_details_block_from_db(lobby_details: LobbyDetails) -> list[Any]:
    """
    Attempt to format general lobby details from database (CACHED data)

    :return:
    """
    formatted_msg = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Dominions Times"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " :freak_lord: *Update* :freak_lord: 🟢 *CACHED*",
            },
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": "🟢 Cached data (updates every 15 minutes)"}],
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{lobby_details.server_info}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"Turn: {lobby_details.turn}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{lobby_details.time_left}"},
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Player List*"}},
    ]
    return formatted_msg


def create_nations_block_from_db(player_list: list) -> list:
    player_blocks = []

    for player in player_list:
        player.turn_emoji = get_emoji(turn_status=player.turn_status)

        player_name_string = f" - {player.nickname}" if player.nickname else ""

        nation_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{player.turn_emoji} - *{player.name}*{player_name_string}",
            },
        }

        player_blocks.append(nation_section)
    return player_blocks
