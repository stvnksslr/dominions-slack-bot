def create_nations_block(nations):
    """
    Attempts to create and format a slack modal

    :param nations:
    :return:
    """
    player_blocks = []

    for player in nations:
        nation_name = player.name
        turn_status = player.turn_played.name
        player_type = player.controller.name

        if player_type == "Bot":
            turn_status_emoji = ":robot_face:"
        elif (
            player_type == "eliminated_player"
            or player_type == "Defeated_Duplicate"
            or player_type == "Defeated_this_turn"
            or player_type == "Defeated"
        ):
            turn_status_emoji = ":skull:"
        elif turn_status == "NotSubmitted":
            turn_status_emoji = ":x:"
        elif turn_status == "PartiallySubmitted":
            turn_status_emoji = ":question:"
        else:
            turn_status_emoji = ":white_check_mark:"

        nation_section = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f" {turn_status_emoji} *{nation_name}*"},
        }

        player_blocks.append(nation_section)
    return player_blocks


def create_game_details_block(game_name, turn, remaining_time):
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
            "text": {"type": "mrkdwn", "text": f"{game_name} Turn: {turn}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"Remaining Hours: {remaining_time}"},
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Player List*"}},
    ]
    return formatted_msg
