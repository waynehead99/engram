#!/usr/bin/env python3
"""Gmail CLI — inbox, search, read, send, reply.

Usage:
    python3 gmail.py <command> [json_args]

Commands:
    inbox   - List recent inbox messages
    search  - Search with Gmail query syntax
    read    - Read full message content
    send    - Send a new email
    reply   - Reply to a message (preserves thread)
"""

import base64
import json
import sys
from email.mime.text import MIMEText
from html.parser import HTMLParser

from googleapiclient.discovery import build

# Allow importing google_auth from same directory
sys.path.insert(0, sys.path[0])
from google_auth import get_credentials


class HTMLTextExtractor(HTMLParser):
    """Simple HTML to plain text converter."""

    def __init__(self):
        super().__init__()
        self._text = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True
        elif tag == "br":
            self._text.append("\n")
        elif tag in ("p", "div", "tr", "li"):
            self._text.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._text.append(data)

    def get_text(self):
        return "".join(self._text).strip()


def html_to_text(html: str) -> str:
    extractor = HTMLTextExtractor()
    extractor.feed(html)
    return extractor.get_text()


def get_service():
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)


def get_header(headers: list, name: str) -> str:
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def extract_body(payload: dict) -> str:
    """Extract plain text body from message payload."""
    # Simple single-part message
    if payload.get("body", {}).get("data"):
        mime = payload.get("mimeType", "")
        data = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        if mime == "text/html":
            return html_to_text(data)
        return data

    # Multipart — look for text/plain first, then text/html
    parts = payload.get("parts", [])
    plain_text = None
    html_text = None

    for part in parts:
        mime = part.get("mimeType", "")
        if mime == "multipart/alternative" or mime.startswith("multipart/"):
            # Recurse into nested multipart
            result = extract_body(part)
            if result:
                return result
        elif mime == "text/plain" and part.get("body", {}).get("data"):
            data = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            plain_text = data
        elif mime == "text/html" and part.get("body", {}).get("data"):
            data = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            html_text = data

    if plain_text:
        return plain_text
    if html_text:
        return html_to_text(html_text)

    # Last resort: recurse all parts
    for part in parts:
        result = extract_body(part)
        if result:
            return result

    return ""


def cmd_inbox(args: dict):
    """List recent inbox messages."""
    max_results = args.get("max", 10)
    unread_only = args.get("unread_only", False)

    service = get_service()
    label_ids = ["INBOX"]
    if unread_only:
        label_ids.append("UNREAD")

    results = service.users().messages().list(
        userId="me", labelIds=label_ids, maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        print(json.dumps({"messages": [], "count": 0}))
        return

    output = []
    for msg_stub in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_stub["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = msg.get("payload", {}).get("headers", [])
        label_ids_msg = msg.get("labelIds", [])

        output.append({
            "id": msg["id"],
            "threadId": msg.get("threadId", ""),
            "from": get_header(headers, "From"),
            "subject": get_header(headers, "Subject"),
            "date": get_header(headers, "Date"),
            "snippet": msg.get("snippet", ""),
            "unread": "UNREAD" in label_ids_msg,
        })

    print(json.dumps({"messages": output, "count": len(output)}))


def cmd_search(args: dict):
    """Search with Gmail query syntax."""
    query = args.get("query", "")
    max_results = args.get("max", 10)

    if not query:
        print(json.dumps({"error": "Missing 'query' argument", "type": "invalid_args"}))
        return

    service = get_service()
    results = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        print(json.dumps({"messages": [], "count": 0}))
        return

    output = []
    for msg_stub in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_stub["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = msg.get("payload", {}).get("headers", [])
        label_ids_msg = msg.get("labelIds", [])

        output.append({
            "id": msg["id"],
            "threadId": msg.get("threadId", ""),
            "from": get_header(headers, "From"),
            "subject": get_header(headers, "Subject"),
            "date": get_header(headers, "Date"),
            "snippet": msg.get("snippet", ""),
            "unread": "UNREAD" in label_ids_msg,
        })

    print(json.dumps({"messages": output, "count": len(output)}))


def cmd_read(args: dict):
    """Read full message content."""
    msg_id = args.get("id", "")
    if not msg_id:
        print(json.dumps({"error": "Missing 'id' argument", "type": "invalid_args"}))
        return

    service = get_service()
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="full"
    ).execute()

    headers = msg.get("payload", {}).get("headers", [])
    body = extract_body(msg.get("payload", {}))

    print(json.dumps({
        "id": msg["id"],
        "threadId": msg.get("threadId", ""),
        "from": get_header(headers, "From"),
        "to": get_header(headers, "To"),
        "cc": get_header(headers, "Cc"),
        "subject": get_header(headers, "Subject"),
        "date": get_header(headers, "Date"),
        "message_id": get_header(headers, "Message-ID"),
        "body": body,
        "labels": msg.get("labelIds", []),
    }))


def cmd_send(args: dict):
    """Send a new email."""
    to = args.get("to", "")
    subject = args.get("subject", "")
    body = args.get("body", "")

    if not to:
        print(json.dumps({"error": "Missing 'to' argument", "type": "invalid_args"}))
        return
    if not subject:
        print(json.dumps({"error": "Missing 'subject' argument", "type": "invalid_args"}))
        return

    service = get_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    result = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()

    print(json.dumps({
        "status": "sent",
        "id": result.get("id", ""),
        "threadId": result.get("threadId", ""),
    }))


def cmd_reply(args: dict):
    """Reply to a message, preserving thread."""
    msg_id = args.get("id", "")
    body = args.get("body", "")

    if not msg_id:
        print(json.dumps({"error": "Missing 'id' argument", "type": "invalid_args"}))
        return

    service = get_service()

    # Fetch original message for thread context
    original = service.users().messages().get(
        userId="me", id=msg_id, format="metadata",
        metadataHeaders=["From", "Subject", "Message-ID", "To"]
    ).execute()

    orig_headers = original.get("payload", {}).get("headers", [])
    thread_id = original.get("threadId", "")
    orig_message_id = get_header(orig_headers, "Message-ID")
    orig_subject = get_header(orig_headers, "Subject")
    orig_from = get_header(orig_headers, "From")

    # Build reply subject
    reply_subject = orig_subject
    if not reply_subject.lower().startswith("re:"):
        reply_subject = f"Re: {reply_subject}"

    message = MIMEText(body)
    message["to"] = orig_from
    message["subject"] = reply_subject
    if orig_message_id:
        message["In-Reply-To"] = orig_message_id
        message["References"] = orig_message_id

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    result = service.users().messages().send(
        userId="me", body={"raw": raw, "threadId": thread_id}
    ).execute()

    print(json.dumps({
        "status": "sent",
        "id": result.get("id", ""),
        "threadId": result.get("threadId", ""),
        "in_reply_to": msg_id,
    }))


COMMANDS = {
    "inbox": cmd_inbox,
    "search": cmd_search,
    "read": cmd_read,
    "send": cmd_send,
    "reply": cmd_reply,
}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": f"Usage: python3 gmail.py <command> [json_args]\nCommands: {', '.join(COMMANDS.keys())}",
            "type": "usage",
        }))
        sys.exit(1)

    command = sys.argv[1]
    if command not in COMMANDS:
        print(json.dumps({
            "error": f"Unknown command: {command}. Available: {', '.join(COMMANDS.keys())}",
            "type": "unknown_command",
        }))
        sys.exit(1)

    # Parse optional JSON args
    args = {}
    if len(sys.argv) >= 3:
        try:
            args = json.loads(sys.argv[2])
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON args: {e}", "type": "json_error"}))
            sys.exit(1)

    try:
        COMMANDS[command](args)
    except Exception as e:
        print(json.dumps({"error": str(e), "type": "api_error"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
