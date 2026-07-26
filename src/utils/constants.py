from os import getenv

from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    """Fail with the variable name, rather than an opaque slack/tortoise error deep into startup."""
    value = getenv(name)
    if not value:
        msg = f"required environment variable {name} is not set"
        raise RuntimeError(msg)
    return value


SLACK_BOT_TOKEN = _required("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = _required("SLACK_APP_TOKEN")

DB_URI = _required("DB_URI")
