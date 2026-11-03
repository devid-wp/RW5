# Class schedule research

Gen2 v4.23 lists separate Hour, Minute and Week sources for type 465. ImageList can select a bitmap from one source value. No verified interface combines weekday and time, accepts lesson data, calculates the next lesson or countdown, or derives lesson progress. Container and selector shapes appear in the database, but a working timetable condition for device 465 has not been established. The desktop Python schedule model stays separate from the face.

The released class card shows Schedule unavailable. A viable architecture is to evaluate the timetable on a phone and deliver lesson transitions through watch notifications, subject to the user's notification settings. Autonomous display would require a supported watch app with local schedule storage and clock access. App installation and watch-face integration for device 465 need separate verification.

[EasyFace ImageList](https://github.com/m0tral/EasyFace/wiki/ImageListRU) · [EasyFace Lua examples and target models](https://github.com/m0tral/MiWatchLuaWatchfaces)

## Weekly schedule implementation

Edit bells, days and rotation in schedule.json. The desktop evaluator uses Europe/Kyiv and counts seven-day intervals from 2026-11-05. Run python tools/render_schedule_preview.py after generating the face to render three desktop examples. The previews use sample sensor readings and never become compiler inputs.

Gen2 ImageList can select an image from an individual device source such as Hour, Minute or Week. No verified facility on device 465 exposes the week parity, combines those sources into timetable rules or computes a countdown or progress from an arbitrary lesson boundary. An indexed hour or weekday image alone cannot express this timetable. The production class card therefore retains its existing availability notice.

A phone can compute the next transition and post a local notification at each lesson or break boundary. On the official paired Mi Fitness path, first enable forwarding for the chosen reminder app and verify one test notification on the watch. This can show current or next class on the watch as a notification. Persistent on-face text, live countdown and operation without the phone remain unverified.
