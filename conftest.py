"""Dummy credentials so importing src.utils.constants doesn't require a real .env under test."""

from os import environ

environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test")
environ.setdefault("SLACK_APP_TOKEN", "xapp-test")
environ.setdefault("DB_URI", "sqlite://:memory:")
