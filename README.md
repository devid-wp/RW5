# SchoolFace

Watch face for the standard Redmi Watch 5 (EasyFace DeviceType 465, 432×514), with a Python schedule engine and a separate Kotlin Android companion.

## Linux

Install JDK 17, Android SDK Platform 35, Build Tools 34.0.0, and Platform Tools. Set JAVA_HOME and ANDROID_HOME to your installation paths. The first Gradle build needs network access to download dependencies.

From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install Pillow tzdata
python -m unittest discover -s tests -v
cd android-companion
./gradlew :app:testDebugUnitTest :app:assembleDebug
adb devices
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

Enable USB debugging on the Android test phone and approve its ADB authorization prompt. The APK is the phone companion. Its watch transport is Unsupported.

The compiled watch face is output/SchoolFace.face. Open output/SchoolFace.fprj with its adjacent output/images directory in the EasyFace bundle that supports device 465. The .face is a distribution artifact, not a compiler input. Recompilation uses EasyFace Gen2 v4.23 on Windows. Native Linux compilation has not been verified.

Verify that the watch is the standard Redmi Watch 5 (not Active or Lite), and that the compiler identifies the target as RedmiWatch5. Compiler success does not verify installation. Official Mi Fitness does not document local .face import. Use only a confirmed installation channel for your device and firmware, then compare date, time, steps, battery and pulse with the built-in screens. See docs/COMPATIBILITY.md and docs/DYNAMIC_SCHEDULE_RESEARCH.md.
The editor project can contain a trailing separator in a numeric BitmapList. Gen2 v4.23 treats it as an empty image filename. The bundled face was compiled from a temporary copy with those separators removed. The editor project is preserved.
