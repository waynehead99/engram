"""Shared Google OAuth2 authentication helper.

Builds credentials from environment variables in ~/.openclaw/.env.
Used by gmail.py and calendar.py via: from google_auth import get_credentials
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials

ENV_PATH = Path.home() / ".openclaw" / ".env"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


def get_credentials() -> Credentials:
    """Build Google OAuth2 credentials from env vars.

    Loads GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN
    from ~/.openclaw/.env and returns a Credentials object.
    """
    load_dotenv(ENV_PATH)

    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")

    missing = []
    if not client_id:
        missing.append("GOOGLE_CLIENT_ID")
    if not client_secret:
        missing.append("GOOGLE_CLIENT_SECRET")
    if not refresh_token:
        missing.append("GOOGLE_REFRESH_TOKEN")

    if missing:
        print(
            f'{{"error": "Missing env vars: {", ".join(missing)}", "type": "auth_error"}}',
            file=sys.stdout,
        )
        sys.exit(1)

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )

    return creds
