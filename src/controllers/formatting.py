from typing import List

from src.models.dataclasses.snek_server_details import SnekServerDetails


def create_nations_block(nations) -> List:
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


def create_game_details_block(game_name, turn, remaining_time, port) -> List:
    """
    Attempt to format general server details

    :param game_name:
    :param turn:
    :param remaining_time:
    :param port:
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
            "text": {"type": "mrkdwn", "text": f"{game_name} Turn: {turn}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"port: {port}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"Remaining Hours: {remaining_time}"},
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Player List*"}},
    ]
    return formatted_msg


def format_server_details(details: SnekServerDetails) -> List:
    """
    Formats a general rundown of all the server settings as tracked by snek.earth

    :param details:
    :return:
    """
    formatted_msg = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Server Settings"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " :sweden: *Update* :sweden:",
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"Name: {details.name}"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "plain_text", "text": f"Id: {details.game_id}", "emoji": True},
                {
                    "type": "plain_text",
                    "text": f"Era: {details.era.name}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Hours: {details.hours}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Hall of Fame Length: {details.hall_of_fame}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Independents strength: {details.independents_strength}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Magic Sites: {details.magic_sites}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Event Rarity: {details.event_rarity}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Richness: {details.richness}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Resources: {details.resources}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Starting Province: {details.starting_province}",
                    "emoji": True,
                },
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "plain_text",
                    "text": f"Victory Condition: {details.victory_condition}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Required Ascension Points: {details.required_ap}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Amount of Level 1 Thrones: {details.lvl_1_thrones}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Amount of Level 2 Thrones: {details.lvl_2_thrones}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Amount of Level 3 Thrones: {details.lvl_3_thrones}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Total VP: {details.total_vp}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Required VP: {details.required_vp}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"State: {details.state}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"User Id: {details.user_id}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Research: {details.research}",
                    "emoji": True,
                },
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "plain_text",
                    "text": f"Supplies: {details.supplies}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Renaming: {details.renaming}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Team Game: {details.team_game}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"No Art Rest: {details.no_art_rest}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Clustered: {details.clustered}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Score Graph: {details.score_graphs}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"No Nation Info: {details.no_nation_info}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Map Id: {details.map_id}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Status: {details.status}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Short Name: {details.shortname}",
                    "emoji": True,
                },
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "plain_text",
                    "text": f"Summer VP: {details.summer_vp}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Capital VP: {details.capital_vp}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Cataclysm on Turn: {details.cataclysm}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Globals: {details.max_globals}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Story Events: {details.story_events}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"No Random Research: {details.no_rand_research}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Recruitment: {details.recruitment}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Mod List: {details.mods}",
                    "emoji": True,
                },
                {
                    "type": "plain_text",
                    "text": f"Nation Rules List: {details.nation_rules}",
                    "emoji": True,
                },
            ],
        },
    ]
    return formatted_msg
