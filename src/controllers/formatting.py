from src.models import LobbyDetails


def create_nations_block(player_list) -> list:
    """
    Attempts to create and format a slack modal

    :param nations:
    :return:
    """
    player_blocks = []

    for player in player_list:

        nation_section = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{player.turn_status}  *{player.name}*"},
        }

        player_blocks.append(nation_section)
    return player_blocks


def create_game_details_block(lobby_details: LobbyDetails):
    """
    Attempt to format general server details

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
