# SchoolFace build

On Windows, use Python 3 with Pillow and tzdata. From the project root run:

```powershell
python tools/build.py
python tools/validate.py
python -m unittest discover -s tests -v
```

The build creates the 432×514 backdrop, transparent digit sprites and calendar labels in output/images, writes output/SchoolFace.fprj and renders output/SchoolFace-preview.png. Gen2 v4.23 compiles output/SchoolFace.face. Use --no-compile to regenerate the source project and simulation alone.

The preview uses sample readings. The compiled project uses device sources for the calendar, 24-hour time, steps, battery and pulse. The class card shows that schedule data is unavailable. The sources RW5.original.fprj and samples/widgets.fprj are read-only inputs.
