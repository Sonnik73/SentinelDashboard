import json
import os
from pathlib import Path


# Credentials must never land in config/dashboard.json - that file is tracked
# in git, so anything written there ends up in the repository (and on GitHub).
# This file is covered by .gitignore's "config/local.*" rule instead, which is
# what the placeholder rule there was reserved for.
SECRETS_FILE = Path("config/local.json")


def load_secrets():
    if not SECRETS_FILE.exists():
        return {}

    try:
        with open(SECRETS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        # A corrupt secrets file falls back to the environment rather than
        # taking the server down, same principle as a broken dashboard.json.
        return {}


def save_secrets(secrets: dict):
    SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(SECRETS_FILE, "w", encoding="utf-8") as file:
        json.dump(secrets, file, ensure_ascii=False, indent=4)

    # A world-readable file would expose the camera password to every account
    # on the machine.
    SECRETS_FILE.chmod(0o600)


def get_secret(key: str, default: str = "") -> str:
    """A value set through the UI wins over the environment variable, so a
    password just typed into Settings takes effect without touching how the
    server was launched. Existing env-var-only setups keep working untouched."""
    value = load_secrets().get(key)

    if value:
        return value

    return os.environ.get(key, default)


def set_secret(key: str, value: str):
    secrets = load_secrets()

    if value:
        secrets[key] = value
    else:
        # An empty value removes the stored secret and lets the environment
        # variable (if any) take over again.
        secrets.pop(key, None)

    save_secrets(secrets)
