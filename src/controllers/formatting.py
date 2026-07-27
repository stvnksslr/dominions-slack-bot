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
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f":bulb: *Suggestion*\n{suggestion}"}})

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


def create_game_details_block(lobby_details: LobbyDetails, game_name: str | None = None) -> list[dict[str, Any]]:
    """
    Header card for a game status message — identical whether the data came from the web or the cache.

    :param lobby_details: Game lobby details
    :param game_name: Name of the game; when known, action buttons are attached
    :return: List of Slack blocks
    """
    # server_info is the raw scraped line — only used when we don't know the game's real name
    title = game_name or lobby_details.server_info
    subtitle = f"Turn {lobby_details.turn}"
    if lobby_details.time_left:
        subtitle += f" · {lobby_details.time_left}"

    formatted_msg: list[dict[str, Any]] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Dominions Times"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f":freak_lord: *{title}* :freak_lord:\n{subtitle}"},
        },
    ]

    if game_name:
        elements: list[dict[str, Any]] = [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": ":arrows_counterclockwise: Refresh", "emoji": True},
                "value": game_name,
                "action_id": "refresh_game_status",
                "style": "primary",
            },
        ]
        # no point offering to set primary on the game that already is one
        if not lobby_details.is_primary:
            elements.append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": ":star: Set Primary", "emoji": True},
                    "value": game_name,
                    "action_id": "set_primary_game",
                }
            )

        formatted_msg.append({"type": "actions", "elements": elements})

    formatted_msg.append({"type": "divider"})
    formatted_msg.append({"type": "section", "text": {"type": "mrkdwn", "text": "*Player List*"}})
    return formatted_msg


def create_nations_block(player_list: list) -> list[dict[str, Any]]:
    player_blocks = []

    for player in player_list:
        turn_emoji = get_emoji(turn_status=player.turn_status)

        # web rows carry the full "Ermor, Ashen Empire" title, db rows the short name — show the short one either way
        nation = player.name.split(",")[0].strip()
        player_name_string = f" - {player.nickname}" if player.nickname else ""

        nation_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{turn_emoji} - *{nation}*{player_name_string}",
            },
        }

        player_blocks.append(nation_section)
    return player_blocks
