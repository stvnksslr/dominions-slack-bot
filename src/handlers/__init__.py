"""
Handlers package for interactive components
"""

from .interactions import (
    handle_add_game_modal_submit,
    handle_refresh_game_status,
    handle_remove_game_modal_submit,
    handle_set_primary_game,
    handle_set_primary_modal_submit,
    open_add_game_modal,
    open_remove_game_modal,
    open_set_primary_modal,
)

__all__ = [
    "handle_add_game_modal_submit",
    "handle_refresh_game_status",
    "handle_remove_game_modal_submit",
    "handle_set_primary_game",
    "handle_set_primary_modal_submit",
    "open_add_game_modal",
    "open_remove_game_modal",
    "open_set_primary_modal",
]
