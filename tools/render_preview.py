"""Render a labelled visual simulation from the generated XML and PNG resources.

Demo values exist only in this file. This is not an EasyFace or watch runtime.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

DEMO = {811: 10, 1011: 41, 1812: 2, 1012: 11, 821: 7142, 841: 95, 822: 75, 2012: 1}


def resource(project: Path, name: str) -> Image.Image:
    path = project.parent / "images" / name
    if not path.is_file():
        raise FileNotFoundError(path)
    return Image.open(path).convert("RGBA")


def render(project: Path, destination: Path) -> None:
    root = ET.parse(project).getroot()
    if root.get("DeviceType") != "465":
        raise ValueError("Preview supports only Redmi Watch 5")
    canvas = Image.new("RGBA", (432, 514), "#0B0D14")
    for widget in root.findall("./Screen/Widget"):
        shape, name = widget.get("Shape"), widget.get("Name")
        x, y = int(widget.get("X")), int(widget.get("Y"))
        width, height = int(widget.get("Width")), int(widget.get("Height"))
        if shape == "30":
            sprite = resource(project, widget.get("Bitmap"))
            if sprite.size != (width, height):
                raise ValueError(f"{name}: image size differs from widget box")
            canvas.alpha_composite(sprite, (x, y))
        elif shape == "31":
            index = DEMO[int(widget.get("Index_Src"))]
            options = dict((int(match.group(1)), match.group(2)) for item in widget.get("BitmapList").split("|")
                           if (match := re.fullmatch(r"\((\d+)\):(.+)", item)))
            sprite = resource(project, options[index])
            canvas.alpha_composite(sprite, (x, y))
        elif shape == "32":
            source = int(widget.get("Value_Src"))
            digits = int(widget.get("Digits"))
            value = str(DEMO[source]).zfill(digits)
            if widget.get("Blanking") == "1":
                value = value.lstrip("0") or "0"
            sprites = [resource(project, widget.get("BitmapList").split("|")[int(d)]) for d in value]
            spacing = int(widget.get("Spacing", "0"))
            total = sum(sprite.width for sprite in sprites) + spacing * (len(sprites) - 1)
            if total > width or any(sprite.height > height for sprite in sprites):
                raise ValueError(f"{name}: digit sprites exceed widget box")
            alignment = int(widget.get("Alignment", "0"))
            cursor = x + (width - total if alignment == 2 else (width - total) // 2 if alignment == 1 else 0)
            for sprite in sprites:
                canvas.alpha_composite(sprite, (cursor, y))
                cursor += sprite.width + spacing
        else:
            raise ValueError(f"Unsupported widget in visual simulation: {shape}")

    draw = ImageDraw.Draw(canvas)
    try:
        label_font = ImageFont.truetype("arialbd.ttf", 10)
    except OSError:
        label_font = ImageFont.load_default()
    draw.text((116, 477), "DEMO PREVIEW  ·  NOT LIVE WATCH DATA", font=label_font, fill="#8B7CFF")
    canvas.convert("RGB").save(destination, optimize=True)
    print(f"Visual simulation: {destination}")


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[1] / "output" / "SchoolFace.fprj"
    render(project, project.with_name("SchoolFace-preview.png"))

