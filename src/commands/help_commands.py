from json import dumps

from .base import Command


class HelpCommand(Command):
    async def execute(self, command: str = "") -> str:
        if command == "game":
            blocks = [
                {"type": "header", "text": {"type": "plain_text", "text": "Game Commands Help"}},
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Usage:* `/dom game [subcommand] [arguments]`",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Subcommands:*\n"
                        "• `add [game_name]` - Add a new game to track\n"
                        "• `remove [game_name]` - Remove a game from tracking\n"
                        "• `nickname [game_name] [nickname]` - Set a nickname for a game\n"
                        "• `list` - List all active games\n"
                        "• `primary [game_name]` - Set a game as the primary game\n"
                        "• `status [game_name] [active|inactive]` - Set a game's active status",
                    },
                },
            ]
            return dumps(blocks)

        if command == "player":
            blocks = [
                {"type": "header", "text": {"type": "plain_text", "text": "Player Command Help"}},
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Usage:* `/dom player [game_name] [nation] [player_name]`",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Associate a player name with a nation in a specific game.\n\n"
                        "*Example:*\n`/dom player MyGame Ermor @john`",
                    },
                },
            ]
            return dumps(blocks)

        if command in ["check", "turn"]:
            cmd_info = {
                "check": {
                    "title": "Check Command Help",
                    "usage": "`/dom check [game_name]` or `/check [game_name]`",
                    "description": "Fetch the current status of a game from the Dominions server (🔴 LIVE data).\n\n"
                    "This command scrapes the game's webpage directly for real-time information.",
                },
                "turn": {
                    "title": "Turn Command Help",
                    "usage": "`/dom turn` or `/turn`",
                    "description": "Display the current turn status for the primary game (🟢 CACHED data).\n\n"
                    "This command uses the database cache, which updates every 15 minutes.",
                },
            }
            info = cmd_info[command]
            blocks = [
                {"type": "header", "text": {"type": "plain_text", "text": info["title"]}},
                {"type": "divider"},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Usage:* {info['usage']}"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": info["description"]}},
            ]
            return dumps(blocks)

        if not command:
            blocks = [
                {"type": "header", "text": {"type": "plain_text", "text": "Dominions 6 Slack Bot Help"}},
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":game_die: *Available Commands*",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Game Management*\n"
                        "`/dom game` - Manage tracked games\n"
                        "`/dom check [game]` - Get live game status 🔴\n"
                        "`/dom turn` - Get cached status for primary game 🟢",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Player Management*\n"
                        "`/dom player [game] [nation] [name]` - "
                        "Associate players with nations",
                    },
                },
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "For detailed help on a command, use: `/dom help [command]`\n"
                            "Example: `/dom help game`",
                        }
                    ],
                },
            ]
            return dumps(blocks)

        # Unknown command
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":x: No help available for '{command}'\n\nUse `/dom help` for general help.",
                },
            }
        ]
        return dumps(blocks)
