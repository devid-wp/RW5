"""Generate cumulative EasyFace opening probes alongside the original image assets."""
from copy import deepcopy
import xml.etree.ElementTree as ET

from build import OUT, SAMPLE, write_project


def main() -> None:
    project = ET.parse(OUT / "SchoolFace.fprj").getroot()
    screen = project.find("Screen")
    widgets = {widget.get("Name"): widget for widget in screen}
    probe = ET.parse(SAMPLE).getroot()
    probe_screen = probe.find("Screen")
    sample_hour = probe_screen.find("Widget")
    hour = deepcopy(widgets["Hour"])
    hour.set("Digits", sample_hour.get("Digits"))
    hour.set("Width", "66")
    probe_screen.remove(sample_hour)
    probe_screen.append(hour)
    write_project(probe, OUT / "EasyFace-check-01-hour.fprj")

    for index, names in enumerate((
        ("Background",),
        ("TimeColon", "Day", "Minute", "Steps", "Battery", "BPM"),
        ("Weekday",),
        ("Month",),
    ), 2):
        if index == 3:
            hour.attrib.update(widgets["Hour"].attrib)
        for name in names:
            probe_screen.append(deepcopy(widgets[name]))
        write_project(probe, OUT / f"EasyFace-check-0{index}-{names[-1].lower()}.fprj")
    probe_screen.attrib.update(screen.attrib)
    write_project(probe, OUT / "EasyFace-check-06-screen-metadata.fprj")


if __name__ == "__main__":
    main()
