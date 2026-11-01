# YT Songs builder

Rebrands a YouTube Music APK as **YT Songs** (new name + your music-note icon) for personal use.
Resource-only edit: classes.dex is untouched. The package name stays `com.google.android.apps.youtube.music`.

## Option A - GitHub Actions (no PC tools needed)
1. Create a PRIVATE repo and push this folder, with the APK saved as `input/ytmusic.apk`
   (use git on the command line: the APK is ~72 MB, over the 25 MB web-upload limit, under the 100 MB git limit).
2. Actions tab -> "Build YT Songs" -> Run workflow.
3. Download the `YT-Songs` artifact -> unzip -> install `YT-Songs.apk`.
   If the build fails on resources, re-run with a newer apktool version in the input box.

## Option B - on your PC
Needs: JDK 17+, Python 3 + `pip install pillow`, Android SDK build-tools (zipalign, apksigner), apktool.jar in this folder.
    cp your-ytmusic.apk input/ytmusic.apk
    ./build.sh            # result: out/YT-Songs.apk

## Notes
- Signed with `keystore/yts.jks` (password `ytsongs123`, personal use only). Keep the same keystore so builds can update each other.
- It is signed with a different key than Google's, so uninstall the original YouTube Music first.
- Sign-in / Play Integrity features may not work on a re-signed build.
- Change the name with `APP_NAME="Other Name" ./build.sh`.
