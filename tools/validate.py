from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from PIL import Image

from schedule import load

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCES = {"Weekday": ("31", "Index_Src", 2012), "Day": ("32", "Value_Src", 1812),
                    "Month": ("31", "Index_Src", 1012), "Hour": ("32", "Value_Src", 811),
                    "Minute": ("32", "Value_Src", 1011), "Steps": ("32", "Value_Src", 821),
                    "Battery": ("32", "Value_Src", 841), "BPM": ("32", "Value_Src", 822)}


def main() -> int:
    load(ROOT / "schedule.json")
    original = ET.parse(ROOT / "RW5.original.fprj").getroot()
    if original.tag != "FaceProject" or original.get("DeviceType") != "465":
        raise ValueError("Original project must target Redmi Watch 5 (465)")
    if (ROOT / "output" / "SchoolFace.fprj").exists():
        generated = ET.parse(ROOT / "output" / "SchoolFace.fprj").getroot()
        if generated.get("DeviceType") != "465":
            raise ValueError("Generated project targets another device")
        screen = generated.find("Screen")
        bitmap = screen.get("Bitmap")
        if bitmap and not (ROOT / "output" / "images" / bitmap).is_file():
            raise ValueError(f"Missing bitmap: {bitmap}")
        with Image.open(ROOT / "output" / "images" / bitmap) as image:
            if image.size != (432, 514):
                raise ValueError("Bitmap must be 432x514 for Redmi Watch 5")
        widgets = screen.findall("Widget")
        names = {widget.get("Name") for widget in widgets}
        if len(names) != len(widgets) or not set(EXPECTED_SOURCES).issubset(names) or "Second" in names:
            raise ValueError("Missing, duplicate, or unverified dynamic widget")
        rectangles = []
        for widget in widgets:
            x, y = int(widget.get("X")), int(widget.get("Y"))
            width, height = int(widget.get("Width")), int(widget.get("Height"))
            if x < 0 or y < 0 or width < 1 or height < 1 or x + width > 432 or y + height > 514:
                raise ValueError(f"Widget outside screen: {widget.get('Name')}")
            if widget.get("Name") != "Background":
                rectangles.append((widget.get("Name"), x, y, x + width, y + height))
            if widget.get("Name") in EXPECTED_SOURCES:
                shape, attr, source = EXPECTED_SOURCES[widget.get("Name")]
                if widget.get("Shape") != shape or int(widget.get(attr, "-1")) != source:
                    raise ValueError(f"Wrong source for {widget.get('Name')}")
            if widget.get("Shape") == "30":
                resources = [widget.get("Bitmap")]
            elif widget.get("Shape") == "31":
                pairs = [re.fullmatch(r"\((\d+)\):(.+)", item) for item in widget.get("BitmapList", "").split("|")]
                if any(pair is None for pair in pairs) or {int(pair.group(1)) for pair in pairs} != set(range(7) if widget.get("Name") == "Weekday" else range(1, 13)):
                    raise ValueError("Invalid calendar indices")
                resources = [pair.group(2) for pair in pairs]
            elif widget.get("Shape") == "32":
                resources = widget.get("BitmapList", "").removesuffix("|").split("|")
                if len(resources) != 10 or any(not f.endswith(f"_{i}.png") for i, f in enumerate(resources)):
                    raise ValueError(f"Digital number lacks 10 digits: {widget.get('Name')}")
            else:
                raise ValueError(f"Unknown widget shape: {widget.get('Shape')}")
            for resource in resources:
                if not resource or not (ROOT / "output" / "images" / resource).is_file():
                    raise ValueError(f"Missing widget resource: {resource}")
            if widget.get("Shape") == "32":
                sizes = set()
                glyphs = set()
                for resource in resources:
                    with Image.open(ROOT / "output" / "images" / resource) as sprite:
                        if sprite.mode != "RGBA" or sprite.getchannel("A").getbbox() is None:
                            raise ValueError(f"Invalid transparent digit: {resource}")
                        alpha = sprite.getchannel("A")
                        if alpha.getextrema() != (0, 255):
                            raise ValueError(f"Digit needs transparent background and opaque ink: {resource}")
                        glyphs.add(alpha.tobytes())
                        sizes.add(sprite.size)
                if len(glyphs) != 10:
                    raise ValueError("Digit sprites must have ten distinct masks")
                if len(sizes) != 1:
                    raise ValueError(f"Mismatched digit sizes: {widget.get('Name')}")
                sprite_width, sprite_height = sizes.pop()
                if sprite_width * int(widget.get("Digits")) > width or sprite_height > height:
                    raise ValueError(f"Digit sprites overflow {widget.get('Name')}")
        for i, a in enumerate(rectangles):
            for b in rectangles[i + 1:]:
                if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]:
                    raise ValueError(f"Widget boxes overlap: {a[0]}, {b[0]}")
    face = ROOT / "output" / "SchoolFace.face"
    if face.is_file():
        if face.stat().st_size < 1024 or face.read_bytes()[:4] != bytes.fromhex("5AA53412"):
            raise ValueError("Compiled face header/size is unexpected")
        info = ROOT / "output" / "output" / "SchoolFace.info"
        if not info.is_file() or ET.parse(info).getroot().get("DeciceTypeName") != "RedmiWatch5":
            raise ValueError("Compiler metadata does not name RedmiWatch5")
    print("Configuration and project XML: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
