from typing import Any

from src.models.app.lobby_details import LobbyDetails


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


def create_game_details_block(lobby_details: LobbyDetails) -> list[Any]:
    """
    Attempt to format general lobby details

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
                "text": " :freak_lord: *Update* :freak_lord:",
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{lobby_details.server_info}"},
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Player List*"}},
    ]
    return formatted_msg


def create_game_details_block_from_db(lobby_details: LobbyDetails) -> list[Any]:
    """
    Attempt to format general lobby details from database

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
                "text": " :freak_lord: *Update* :freak_lord:",
            },
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
