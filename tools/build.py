"""Generate an EasyFace XML candidate from the editor-saved widget sample."""
from copy import deepcopy
import argparse
import subprocess
import time
from tempfile import TemporaryFile
import xml.etree.ElementTree as ET
from pathlib import Path

from generate_assets import make, ROOT, OUT
from render_preview import render
from schedule import load

SAMPLE = ROOT / "samples" / "widgets.fprj"
COMPILER = Path(r"C:\Users\galas\Downloads\EasyFace_Gen2_CompilerV423\Compiler.exe")
SOURCE_IDS = {
    "hour": 811, "minute": 1011, "second": 1811,
    "day": 1812, "month": 1012, "steps": 821, "battery": 841, "bpm": 822,
}


def number(screen: ET.Element, example: ET.Element, name: str, source: str,
           x: int, y: int, width: int, height: int, digits: int, group: str) -> None:
    widget = deepcopy(example)
    widget.attrib.update({
        "Name": name, "X": str(x), "Y": str(y), "Width": str(width),
        "Height": str(height), "Digits": str(digits),
        "Value_Src": str(SOURCE_IDS[source]), "BitmapList": "|".join(
            f"{group}_{n}.png" for n in range(10)),
    })
    screen.append(widget)


def image(screen: ET.Element, name: str, bitmap: str, x: int, y: int,
          width: int, height: int) -> None:
    ET.SubElement(screen, "Widget", {
        "Shape": "30", "Name": name, "Bitmap": bitmap,
        "X": str(x), "Y": str(y), "Width": str(width),
        "Height": str(height), "Alpha": "255", "Visible_Src": "0",
    })


def weekday(screen: ET.Element) -> None:
    ET.SubElement(screen, "Widget", {
        "Shape": "31", "Name": "Weekday", "X": "40", "Y": "91",
        "Width": "84", "Height": "42", "Alpha": "255", "Visible_Src": "0",
        "Index_Src": "2012", "DefaultIndex": "0",
        "BitmapList": "|".join(f"({i}):week_{i}.png" for i in range(7)),
    })


def compile_face(target) -> None:
    if not COMPILER.is_file():
        print(f"Compiler not found at {COMPILER}; XML and assets are ready.")
        return
    (OUT / "output").mkdir(exist_ok=True)
    face = OUT / "SchoolFace.face"
    info = OUT / "output" / "SchoolFace.info"
    started = time.time()
    command = [str(COMPILER), "-b", str(target), str(OUT), face.name, "1461256429"]
    timed_out = False
    # ADB may inherit stdout and keep a pipe open after the compiler exits.
    with TemporaryFile() as log:
        try:
            subprocess.run(command, cwd=COMPILER.parent, stdout=log,
                           stderr=subprocess.STDOUT, timeout=20)
        except subprocess.TimeoutExpired:
            timed_out = True
        log.seek(0)
        output = log.read().decode(errors="replace")

    print(output.strip())
    if ("No Errors" in output and face.is_file() and info.is_file()
            and face.stat().st_mtime >= started - 2 and info.stat().st_mtime >= started - 2):
        print(f"Compiler produced {face} ({face.stat().st_size} bytes)")
        if timed_out:
            print("Compiler timed out after creating artifacts during its emulator upload step.")
    else:
        raise RuntimeError("Compiler did not produce fresh, error-free face and info files")


def write_project(project: ET.Element, target: Path) -> None:
    # Match the declaration and layout of the editor-saved sample.
    ET.indent(project, space="    ")
    xml = '<?xml version="1.0" encoding="UTF-8" ?>\n'
    xml += ET.tostring(project, encoding="unicode") + "\n"
    target.write_bytes(xml.replace("\n", "\r\n").encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-compile", action="store_true", help="Only generate XML and assets")
    args = parser.parse_args()
    load(ROOT / "schedule.json")
    if not SAMPLE.is_file():
        raise FileNotFoundError(f"Editor-saved widget sample missing: {SAMPLE}")
    example_root = ET.parse(SAMPLE).getroot()
    example = example_root.find("./Screen/Widget[@Shape='32']")
    if example_root.get("DeviceType") != "465" or example is None or int(example.get("Value_Src", "-1")) != 811:
        raise ValueError("Sample must contain a Redmi Watch 5 Hour Digital Number widget")

    project = ET.parse(ROOT / "RW5.original.fprj").getroot()
    if project.get("DeviceType") != "465":
        raise ValueError("Baseline must target Redmi Watch 5")
    screen = project.find("Screen")
    if screen is None:
        raise ValueError("Baseline has no Screen")
    make()
    screen.set("Title", "SchoolFace")
    screen.set("Bitmap", "background.png")
    image(screen, "Background", "background.png", 0, 0, 432, 514)
    weekday(screen)
    week = screen.find("Widget[@Name='Weekday']")
    week.attrib.update(X="40", Y="28", Width="86", Height="34")
    number(screen, example, "Day", "day", 170, 31, 36, 28, 2, "small")
    ET.SubElement(screen, "Widget", {
        "Shape": "31", "Name": "Month", "X": "208", "Y": "28",
        "Width": "66", "Height": "34", "Alpha": "255", "Visible_Src": "0",
        "Index_Src": "1012", "DefaultIndex": "1",
        "BitmapList": "|".join(f"({i}):month_{i}.png" for i in range(1, 13)),
    })
    number(screen, example, "Hour", "hour", 75, 79, 132, 84, 2, "time")
    image(screen, "TimeColon", "colon.png", 207, 79, 18, 84)
    number(screen, example, "Minute", "minute", 225, 79, 132, 84, 2, "time")
    number(screen, example, "Steps", "steps", 43, 411, 90, 28, 5, "small")
    number(screen, example, "Battery", "battery", 193, 411, 54, 28, 3, "small")
    number(screen, example, "BPM", "bpm", 327, 411, 54, 28, 3, "small")
    for name in ("Steps", "Battery", "BPM"):
        widget = screen.find(f"Widget[@Name='{name}']")
        widget.set("Blanking", "1")
        widget.set("Alignment", "2" if name == "Battery" else "1")

    target = OUT / "SchoolFace.fprj"
    write_project(project, target)
    print(f"Generated candidate: {target}")
    render(target, OUT / "SchoolFace-preview.png")
    if not args.no_compile:
        compile_face(target)
    print("EasyFace GUI and physical-watch behavior have not yet been verified.")


if __name__ == "__main__":
    main()



