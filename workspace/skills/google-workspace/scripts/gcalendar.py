#!/usr/bin/env python3
"""Google Calendar CLI — today, upcoming, search, create.

Usage:
    python3 calendar.py <command> [json_args]

Commands:
    today    - List today's events
    upcoming - List events in the next N days
    search   - Search events by text
    create   - Create a calendar event
"""

import json
import sys
from datetime import datetime, timedelta

from googleapiclient.discovery import build

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# Allow importing google_auth from same directory
sys.path.insert(0, sys.path[0])
from google_auth import get_credentials

TIMEZONE = "America/Chicago"


def get_service():
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)


def format_event(event: dict) -> dict:
    """Format a calendar event for output."""
    start = event.get("start", {})
    end = event.get("end", {})

    return {
        "id": event.get("id", ""),
        "summary": event.get("summary", "(No title)"),
        "start": start.get("dateTime", start.get("date", "")),
        "end": end.get("dateTime", end.get("date", "")),
        "location": event.get("location", ""),
        "description": event.get("description", ""),
        "status": event.get("status", ""),
        "htmlLink": event.get("htmlLink", ""),
        "attendees": [
            {"email": a.get("email", ""), "responseStatus": a.get("responseStatus", "")}
            for a in event.get("attendees", [])
        ],
    }


def cmd_today(args: dict):
    """List today's events."""
    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    service = get_service()
    results = service.events().list(
        calendarId="primary",
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy="startTime",
        timeZone=TIMEZONE,
    ).execute()

    events = results.get("items", [])
    output = [format_event(e) for e in events]

    print(json.dumps({
        "date": now.strftime("%Y-%m-%d"),
        "timezone": TIMEZONE,
        "events": output,
        "count": len(output),
    }))


def cmd_upcoming(args: dict):
    """List events in the next N days."""
    days = args.get("days", 7)
    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    end_date = now + timedelta(days=days)

    service = get_service()
    results = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=end_date.isoformat(),
        singleEvents=True,
        orderBy="startTime",
        timeZone=TIMEZONE,
    ).execute()

    events = results.get("items", [])
    output = [format_event(e) for e in events]

    print(json.dumps({
        "from": now.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d"),
        "timezone": TIMEZONE,
        "events": output,
        "count": len(output),
    }))


def cmd_search(args: dict):
    """Search events by text."""
    query = args.get("query", "")
    days = args.get("days", 30)

    if not query:
        print(json.dumps({"error": "Missing 'query' argument", "type": "invalid_args"}))
        return

    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    end_date = now + timedelta(days=days)

    service = get_service()
    results = service.events().list(
        calendarId="primary",
        q=query,
        timeMin=now.isoformat(),
        timeMax=end_date.isoformat(),
        singleEvents=True,
        orderBy="startTime",
        timeZone=TIMEZONE,
    ).execute()

    events = results.get("items", [])
    output = [format_event(e) for e in events]

    print(json.dumps({
        "query": query,
        "events": output,
        "count": len(output),
    }))


def cmd_create(args: dict):
    """Create a calendar event."""
    summary = args.get("summary", "")
    start = args.get("start", "")
    end = args.get("end", "")

    if not summary:
        print(json.dumps({"error": "Missing 'summary' argument", "type": "invalid_args"}))
        return
    if not start:
        print(json.dumps({"error": "Missing 'start' argument", "type": "invalid_args"}))
        return
    if not end:
        print(json.dumps({"error": "Missing 'end' argument", "type": "invalid_args"}))
        return

    # Determine if all-day event (date-only format: YYYY-MM-DD)
    is_all_day = len(start) == 10 and len(end) == 10

    event_body = {"summary": summary}

    if is_all_day:
        event_body["start"] = {"date": start}
        event_body["end"] = {"date": end}
    else:
        event_body["start"] = {"dateTime": start, "timeZone": TIMEZONE}
        event_body["end"] = {"dateTime": end, "timeZone": TIMEZONE}

    # Optional fields
    if args.get("location"):
        event_body["location"] = args["location"]
    if args.get("description"):
        event_body["description"] = args["description"]
    if args.get("attendees"):
        event_body["attendees"] = [{"email": e} for e in args["attendees"]]

    service = get_service()
    result = service.events().insert(
        calendarId="primary", body=event_body
    ).execute()

    print(json.dumps({
        "status": "created",
        "id": result.get("id", ""),
        "summary": result.get("summary", ""),
        "start": result.get("start", {}),
        "end": result.get("end", {}),
        "htmlLink": result.get("htmlLink", ""),
    }))


COMMANDS = {
    "today": cmd_today,
    "upcoming": cmd_upcoming,
    "search": cmd_search,
    "create": cmd_create,
}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": f"Usage: python3 calendar.py <command> [json_args]\nCommands: {', '.join(COMMANDS.keys())}",
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
