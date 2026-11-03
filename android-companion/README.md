# SchoolFace Companion

Requires JDK 17, Android SDK Platform 35 and Build Tools 34.0.0. Set JAVA_HOME and ANDROID_HOME before running the included Gradle 8.9 wrapper. Open this directory in Android Studio or run from it:

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebug
```

On the RW5 Windows workspace, the local toolchain is under .toolchain. To reuse it from this directory:

```powershell
$root = (Resolve-Path .toolchain).Path
$env:JAVA_HOME = (Get-ChildItem "$root\jdk" -Directory | Select-Object -First 1).FullName
$env:ANDROID_HOME = "$root\android-sdk"
$env:GRADLE_USER_HOME = "$root\gradle-home"
& "$root\gradle\gradle-8.9\bin\gradle.bat" :app:testDebugUnitTest :app:assembleDebug
```
The APK is written to app/build/outputs/apk/debug/app-debug.apk. Gradle needs access to dependency repositories on initial setup. The app has no Internet permission and runs offline.

The build copies ../schedule.json into the APK. Edit the root file and rebuild/install the new APK to change the timetable. Package replacement refreshes the schedule and re-arms the next alarm. The app uses Europe/Kyiv even when the phone's time zone changes.

Background updates use one inexact RTC_WAKEUP alarm. On boot after unlock, clock changes, package replacement, app resume or Refresh, the app recomputes from the actual current time and replaces the pending alarm. The background switch persists via DataStore. The displayed countdown and progress are snapshots. Refresh updates them immediately. Android 12+ can delay inexact alarms up to an hour in ordinary conditions, and battery restrictions can delay them longer. A delayed wake skips obsolete states. No foreground service, exact-alarm access, BLE connection or background polling is used. See [Android alarm scheduling](https://developer.android.com/develop/background-work/services/alarms).

Watch transfer is Unsupported. The app exposes a WatchTransport interface and uses NoOpWatchTransport. Test Update explicitly reports that nothing can be transferred. Xiaomi documents Events syncing and notification forwarding through Mi Fitness, but no supported third-party API for writing a live field into a Redmi Watch 5 face was found. See [Xiaomi Events](https://www.mi.com/global/support/faq/details/KA-527896/) and [research](../docs/DYNAMIC_SCHEDULE_RESEARCH.md).

On a test phone, verify foreground refresh, delayed delivery after sleep, cancellation with Background updates off, and alarm recovery after reboot and unlock. A force-stopped app must be opened again. The watch face remains a separate project.


