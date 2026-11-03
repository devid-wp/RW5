"""Weekly school schedule model. This code runs on the PC, not on the watch."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def minutes(value: str) -> int:
    parsed = dt.datetime.strptime(value, "%H:%M").time()
    return parsed.hour * 60 + parsed.minute


def load(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    if "bells" in config:
        bells = config.pop("bells")
        for day, subjects in config["days"].items():
            if len(subjects) > len(bells):
                raise ValueError(f"{day}: more subjects than bell slots")
            config["days"][day] = [
                {"start": start, "end": end, "subject": subject}
                for (start, end), subject in zip(bells, subjects)
            ]
    validate(config)
    return config


def validate(config: dict) -> None:
    if config.get("mode") not in ("DEMO", "REAL"):
        raise ValueError("mode must be DEMO or REAL")
    ZoneInfo(config["timezone"])
    if config.get("week_starts_on") != "monday":
        raise ValueError("week_starts_on must be monday")
    days = config.get("days")
    if not isinstance(days, dict) or set(days) != set(DAYS):
        raise ValueError("days must contain all seven weekdays")
    for day, lessons in days.items():
        if not isinstance(lessons, list):
            raise ValueError(f"{day}: lessons must be a list")
        previous_end = 0
        for lesson in lessons:
            if set(lesson) != {"start", "end", "subject"}:
                raise ValueError(f"{day}: lesson needs start, end, subject")
            start, end = minutes(lesson["start"]), minutes(lesson["end"])
            if not 0 <= start < end <= 24 * 60 or start < previous_end:
                raise ValueError(f"{day}: invalid or overlapping lesson")
            if not isinstance(lesson["subject"], str) or not lesson["subject"].strip():
                raise ValueError(f"{day}: empty subject")
            previous_end = end


def status(config: dict, instant: dt.datetime) -> dict:
    if instant.tzinfo is None:
        raise ValueError("instant must have timezone")
    local = instant.astimezone(ZoneInfo(config["timezone"]))
    lessons = config["days"][DAYS[local.weekday()]]
    rotation = config.get("rotation")
    if rotation and DAYS[local.weekday()] == rotation["day"]:
        anchor = dt.date.fromisoformat(rotation["anchor"])
        week = (local.date() - anchor).days // 7
        subjects = rotation["subjects"]
        lessons = [dict(lesson) for lesson in lessons]
        lessons[rotation["period"] - 1]["subject"] = subjects[week % len(subjects)]
    labels = {
        "before": "Before School", "lesson": "Current Class", "break": "Break Time",
        "after": "School Finished", "weekend": "No Classes Today",
    }
    now = local.hour * 3600 + local.minute * 60 + local.second

    def result(state, current=None, upcoming=None, start=None, end=None):
        return {
            "state": state, "label": labels[state], "current": current, "next": upcoming,
            "total_lessons": len(lessons),
            "remaining_seconds": end - now if end is not None else None,
            "remaining_minutes": (end - now + 59) // 60 if end is not None else None,
            "progress": (now - start) / (end - start) if start is not None else None,
        }

    if not lessons:
        return result("weekend")
    numbered = [dict(lesson, number=i) for i, lesson in enumerate(lessons, 1)]
    previous_end = None
    for index, lesson in enumerate(numbered):
        start, end = (minutes(lesson[key]) * 60 for key in ("start", "end"))
        if now < start:
            return result("before" if index == 0 else "break",
                          upcoming=lesson, start=previous_end, end=start)
        if now < end:
            upcoming = numbered[index + 1] if index + 1 < len(numbered) else None
            return result("lesson", lesson, upcoming, start, end)
        previous_end = end
    return result("after")
