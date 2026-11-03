"""Render schedule states on desktop without adding lesson data to the face."""
from datetime import datetime
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw

from generate_assets import ROOT, OUT, PURPLE, WHITE, MUTED, SURFACE, font
from render_preview import render, DEMO
from schedule import load, status


def main():
    config = load(ROOT / "schedule.json")
    zone = ZoneInfo(config["timezone"])
    for hour, minute in ((9, 20), (9, 50), (16, 40)):
        instant = datetime(2026, 11, 4, hour, minute, tzinfo=zone)
        state = status(config, instant)
        DEMO.update({811: hour, 1011: minute, 1812: 4, 2012: 3, 1012: 11})
        target = OUT / f"Schedule-preview-{state['state']}.png"
        render(OUT / "SchoolFace.fprj", target)
        with Image.open(target) as source:
            canvas = source.convert("RGB")
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((44, 181, 387, 330), fill=SURFACE)
        draw.text((46, 186), state["label"].upper(), font=font(17, True), fill=PURPLE)
        current, upcoming = state["current"], state["next"]
        if current:
            draw.text((380, 186), f"{current['number']} / {state['total_lessons']}",
                      anchor="rt", font=font(15), fill=MUTED)
        subject = current or upcoming
        if subject:
            draw.text((46, 222), subject["subject"], font=font(23, True), fill=WHITE)
            timing = f"{current['start']}–{current['end']}  ·  " if current else "Starts in "
            draw.text((46, 256), timing + f"{state['remaining_minutes']} min",
                      font=font(16), fill=MUTED)
            draw.rounded_rectangle((46, 283, 386, 291), radius=4, fill="#34364B")
            width = round(340 * state["progress"])
            if width:
                draw.rounded_rectangle((46, 283, 46 + width, 291), radius=4, fill=PURPLE)
            if current and upcoming:
                draw.text((46, 304), f"NEXT: {upcoming['subject']}", font=font(15), fill=MUTED)
        canvas.save(target, optimize=True)


if __name__ == "__main__":
    main()
