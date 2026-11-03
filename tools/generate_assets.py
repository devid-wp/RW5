"""Create static art and transparent digit sprites for the watch widgets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
SIZE = (432, 514)
BG, PURPLE, WHITE, MUTED, SURFACE = "#0B0D14", "#8B7CFF", "#FFFFFF", "#A8A9C8", "#171A26"


def font(size: int, bold: bool = False):
    family = "segoeuib.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(family, size)
    except OSError:
        return ImageFont.load_default()


def pixel_icon(image, xy, rows):
    draw = ImageDraw.Draw(image)
    x, y = xy
    for row, pattern in enumerate(rows.split()):
        for col, pixel in enumerate(pattern):
            if pixel == "#":
                left, top = x + col * 2, y + row * 2
                draw.rectangle((left, top, left + 1, top + 1), fill=PURPLE)

def make() -> None:
    images = OUT / "images"
    images.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((13, 14, 418, 492), radius=39, outline=PURPLE, width=2)
    for y in (73, 363):
        draw.line((39, y, 393, y), fill=PURPLE)
    draw.line((146, 33, 146, 58), fill=PURPLE)
    for row in range(3):
        for col in range(3 - row, 5):
            x, y = 345 + col * 10, 31 + row * 10
            draw.rectangle((x, y, x + 3, y + 3), fill=PURPLE if row == 2 else "#514575")
    draw.rounded_rectangle((27, 174, 405, 349), radius=18, fill=SURFACE, outline=PURPLE)
    pixel_icon(image, (46, 186), ".....##..... ...##..##... .##......##. #..........# .##......##. ..###..###.. ..#..##..#.. ..#......#.. ...######...")
    draw.text((85, 186), "CURRENT CLASS", font=font(17, True), fill=PURPLE)
    draw.text((46, 232), "Schedule unavailable", font=font(27, True), fill=WHITE)
    draw.text((46, 276), "No live class data", font=font(16), fill=MUTED)
    draw.line((46, 312, 386, 312), fill="#34364B")
    for x, right, label in ((27, 149, "STEPS"), (165, 287, "BATTERY"), (303, 405, "BPM")):
        draw.rounded_rectangle((x, 377, right, 472), radius=17, fill=SURFACE, outline="#514575")
        draw.text(((x + right) // 2, 455), label, anchor="mm", font=font(14), fill=MUTED)
    pixel_icon(image, (77, 385), ".......##. ......#### ......#### .##....##. ####...... ####...##. .##....... .......... .##.......")
    pixel_icon(image, (213, 388), ".##########.. #..........#. #..........## #..........## #..........#. .##########..")
    pixel_icon(image, (342, 386), ".###....###. #...#..#...# #....##....# #..........# .#........#. ..#......#.. ...#....#... ....#..#.... .....##.....")

    draw.text((255, 425), "%", anchor="mm", font=font(18, True), fill=WHITE)
    image.save(images / "background.png", optimize=True)

    for group, width, height, scale, font_size in (
        ("time", 66, 84, 3, 29), ("small", 18, 28, 2, 13),
    ):
        for digit in range(10):
            sprite = Image.new("RGBA", (width // scale, height // scale))
            painter = ImageDraw.Draw(sprite)
            painter.fontmode = "1"
            painter.text((sprite.width // 2, sprite.height // 2), str(digit),
                         anchor="mm", font=font(font_size, True), fill=WHITE)
            sprite.resize((width, height), Image.Resampling.NEAREST).save(images / f"{group}_{digit}.png")
    colon = Image.new("RGBA", (18, 84))
    painter = ImageDraw.Draw(colon)
    for y in (24, 52):
        painter.rectangle((4, y, 13, y + 9), fill=WHITE)
    colon.save(images / "colon.png")
    for group, labels, start, size in (
        ("week", "SUN MON TUE WED THU FRI SAT", 0, (86, 34)),
        ("month", "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC", 1, (66, 34)),
    ):
        for index, label in enumerate(labels.split(), start):
            sprite = Image.new("RGBA", size)
            painter = ImageDraw.Draw(sprite)
            if group == "week":
                painter.rounded_rectangle((0, 0, 85, 33), radius=15, fill=SURFACE, outline=PURPLE)
            painter.text((size[0] // 2, 17), label, anchor="mm", font=font(21, True),
                         fill=PURPLE if group == "week" else WHITE)
            sprite.save(images / f"{group}_{index}.png", optimize=True)


if __name__ == "__main__":
    make()

