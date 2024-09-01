from .base import Command


class HelpCommand(Command):
    async def execute(self, command: str = "") -> str:
        help_texts = {
            "game": """
            Game command usage: `/dom game [subcommand] [arguments]`
            Subcommands:
            - add [game_name]: Add a new game to track
            - remove [game_name]: Remove a game from tracking
            - nickname [game_name] [nickname]: Set a nickname for a game
            - list: List all active games
            - primary [game_name]: Set a game as the primary game
            - status [game_name] [active|inactive]: Set a game's active status
            """,
            "player": """
            Player command usage: `/dom player [game_name] [nation] [player_name]`
            Associate a player name with a nation in a specific game.
            """,
            "check": """
            Check command usage: `/check [game_name]`
            Fetch the current status of a game, including player statuses and turn timer.
            """,
            "turn": """
            Turn command usage: `/turn`
            Display the current turn status for all active games.
            """,
        }

        if command in help_texts:
            return f"{command.capitalize()} command help:\n{help_texts[command].strip()}"
        if not command:
            help_text = """
            *Dominions 6 Slack Bot Help*

            Here are the available commands:
            """
            for cmd, text in help_texts.items():
                help_text += f"\n{cmd.capitalize()}:\n{text.strip()}\n"

            help_text += "\nFor more detailed information on a specific command, use: `/dom help [command]`"
            return help_text
        return f"No specific help available for '{command}'. Please use `/dom help` for general help."
