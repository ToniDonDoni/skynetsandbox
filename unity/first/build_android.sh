#!/usr/bin/env bash
# Build the Unity XR project into pupa.apk (Android).
# Requirements: Unity 6000.3.2f1 with Android Build Support modules installed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="$SCRIPT_DIR"
UNITY_CMD="${UNITY_PATH:-}"
OUTPUT_PATH="${OUTPUT_PATH:-$PROJECT_PATH/Builds/Android/pupa.apk}"
LOG_PATH="${LOG_PATH:-$PROJECT_PATH/unity_build.log}"

mkdir -p "$(dirname "$OUTPUT_PATH")"

if [[ "${UNITY_MOCK_BUILD:-0}" == "1" ]]; then
  echo "UNITY_MOCK_BUILD=1 set; generating placeholder APK at $OUTPUT_PATH"
  printf "Mock APK generated on %s\n" "$(date -Is)" > "$OUTPUT_PATH"
else
  if [[ -z "$UNITY_CMD" ]]; then
    echo "UNITY_PATH is not set. Please point UNITY_PATH to the Unity binary (e.g., /home/<user>/Unity/Hub/Editor/6000.3.2f1/Editor/Unity)." >&2
    exit 1
  fi

  if [[ ! -x "$UNITY_CMD" ]]; then
    echo "Unity CLI ($UNITY_CMD) not found or not executable. Install Unity 6000.3.2f1 with Android Build Support and set UNITY_PATH accordingly." >&2
    exit 1
  fi

  "$UNITY_CMD" -batchmode -nographics -projectPath "$PROJECT_PATH" \
    -buildTarget Android -executeMethod UnityEditor.BuildPipeline.BuildPlayer \
    -logFile "$LOG_PATH" -quit \
    -customBuildTarget Android -customBuildName pupa -customBuildPath "$OUTPUT_PATH"
fi

if [[ ! -f "$OUTPUT_PATH" ]]; then
  echo "Build completed but no APK was found at $OUTPUT_PATH" >&2
  exit 1
fi

apk_size_bytes=$(stat --format="%s" "$OUTPUT_PATH")
apk_size_human=$(du -h "$OUTPUT_PATH" | cut -f1)

echo "APK written to $OUTPUT_PATH"
echo "APK size: ${apk_size_human} (${apk_size_bytes} bytes)"
