#!/usr/bin/env bash
# Rebrand a YouTube Music APK as "YT Songs": decode -> patch name/icon -> rebuild -> align -> sign.
# usage: ./build.sh [input.apk]       env: APKTOOL_JAR (default ./apktool.jar), APP_NAME
set -euo pipefail
cd "$(dirname "$0")"

APK="${1:-input/ytmusic.apk}"
APP_NAME="${APP_NAME:-YT Songs}"
APKTOOL_JAR="${APKTOOL_JAR:-apktool.jar}"
[ -f "$APK" ] || { echo "APK not found: $APK"; exit 1; }
[ -f "$APKTOOL_JAR" ] || { echo "apktool jar not found: $APKTOOL_JAR"; exit 1; }

# --- locate Android build-tools (zipalign, apksigner) ---
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
if ! command -v apksigner >/dev/null || ! command -v zipalign >/dev/null; then
  BT=$(ls -d "$SDK"/build-tools/*/ 2>/dev/null | sort -V | tail -1 || true)
  [ -n "$BT" ] || { echo "Install Android build-tools (zipalign/apksigner) or set ANDROID_HOME"; exit 1; }
  export PATH="$BT:$PATH"
fi

rm -rf build && mkdir -p build out
echo "== decode =="
java -jar "$APKTOOL_JAR" d -s -f "$APK" -o build/decoded

echo "== icons =="
python3 scripts/make_icons.py assets/music.png build/icons

echo "== patch =="
python3 scripts/patch.py build/decoded build/icons "$APP_NAME"

echo "== rebuild =="
java -jar "$APKTOOL_JAR" b build/decoded -o build/unsigned.apk

echo "== align + sign =="
zipalign -p -f 4 build/unsigned.apk build/aligned.apk
apksigner sign --ks keystore/yts.jks --ks-pass pass:ytsongs123 --key-pass pass:ytsongs123 \
  --out out/YT-Songs.apk build/aligned.apk
apksigner verify out/YT-Songs.apk && echo "OK -> out/YT-Songs.apk"
