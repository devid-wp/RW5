# Redmi Watch 5 compatibility

This build targets the standard Redmi Watch 5, DeviceType 465, at 432×514. The local Gen2 v4.23 device database provides 811 for 24-hour hours, 1011 for minutes, 1812 for the day, 1012 for the month, 2012 for the weekday, 821 for steps, 841 for battery percentage and 822 for heart rate. Calendar images use Sunday=0 and January=1. On-device refresh and pulse behavior when no reading is available still require verification.

Source 1811 exposes seconds in the database. Compiler acceptance alone cannot establish one-second refresh with the screen awake or its power cost. The released layout omits seconds.

Xiaomi documents catalog downloads and photo customization via Mi Fitness → Device → Manage watch faces → Online → Custom. No official local .face import or conversion route was found. A photo face can use its template's supported readings. It cannot import the SchoolFace widget layout. [Xiaomi customization instructions](https://www.mi.com/my/support/faq/details/KA-528025/)

The EasyFace author describes an Android route through modified Mi Fitness and a community database. That route has not been verified on the user's watch. The emulator is an intermediate test option and does not establish hardware compatibility. [EasyFace](https://github.com/m0tral/EasyFace) · [MiWatchEmulator](https://github.com/m0tral/MiWatchEmulator)

Before a hardware test, confirm the exact model, firmware and an accepted delivery channel. Then verify that the face can be selected and compare calendar, minute rollover, steps, battery and pulse with built-in screens.
