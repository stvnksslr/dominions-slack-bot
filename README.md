# Dominions Slack Bot

[![Build](https://github.com/stvnksslr/dominions-slack-bot/actions/workflows/build.yml/badge.svg)](https://github.com/stvnksslr/dominions-slack-bot/actions/workflows/build.yml)
[![Deploy](https://github.com/stvnksslr/dominions-slack-bot/actions/workflows/deploy.yml/badge.svg)](https://github.com/stvnksslr/dominions-slack-bot/actions/workflows/deploy.yml)

## Dominions 6 Slack Bot

A Slack bot for managing and tracking Dominions 6 games, providing updates and allowing players to interact with game information directly through Slack.

## Features

* Track multiple Dominions 6 games
* Automatically update game status and player turns
* Respond to various Slack commands for game management and information retrieval
* Fun responses to keywords like "grog" and "mad"
* Periodic task to update game information

## Commands

`/dom` is the only slash command. Everything else is a subcommand of it.

* `/dom help [game|player|check|turn]`: Show usage
* `/dom check <game_name>`: Fetch a game's current status from the website (posted to the channel)
* `/dom turn`: Show the cached status for the primary game (posted to the channel)
* `/dom player <game_name> <nation> <player_name>`: Associate a player name with a nation
* `/dom game ...`: Manage tracked games
  * `game add <game_name>`: Add a new game to track
  * `game remove <game_name>`: Remove a game from tracking
  * `game nickname <game_name> <nickname>`: Set a nickname for a game
  * `game list`: List all active games
  * `game primary <game_name>`: Set the game `/dom turn` reports on
  * `game status <game_name> <active|inactive>`: Set a game's active status

Help, errors and confirmations are ephemeral — only the person who ran the command sees them.
Only `/dom check` and `/dom turn` post to the channel.

## Project Structure

* `commands/`: Command handlers for various bot functionalities
* `controllers/`: Logic for parsing commands and formatting responses
* `models/`: Data models for games, players, and lobby details
* `responders/`: Fun response handlers for keywords
* `tasks/`: Background tasks for updating game information
* `utils/`: Utility functions and managers (database, logging, Slack)
* `main.py`: Main entry point for the application

## Setup

1. Clone the repository
2. Install dependencies:

   ```sh
   uv sync
   ```

3. Set up environment variables:
   * `SLACK_BOT_TOKEN`: Your Slack bot token
   * `SLACK_APP_TOKEN`: Your Slack app token
   * `DB_URI`: Database connection URI
   * `LOG_LEVEL`: Logging level (default: INFO)
   * `TURN_UPDATE_CHANNEL`: Channel for turn notifications (default: `#grog_hole`)

   The first three are required; the bot exits at startup naming any that are missing.

4. Run the bot:

   ```sh
   uv run python -m src.main
   ```

## Testing

Unit tests are available in the `*_test.py` files. Run tests using pytest:

```sh
uv run pytest
```
