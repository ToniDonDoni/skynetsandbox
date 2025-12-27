#!/usr/bin/env bash
# End-to-end helper to install dependencies and build the Android APK.
# This script runs install_build_dependencies.sh (with sudo when needed),
# then executes build_android.sh and verifies the APK is present.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
INSTALL_SCRIPT="$PROJECT_DIR/install_build_dependencies.sh"
BUILD_SCRIPT="$PROJECT_DIR/build_android.sh"
APK_PATH="${OUTPUT_PATH:-$PROJECT_DIR/Builds/Android/pupa.apk}"

if [[ ! -x "$INSTALL_SCRIPT" ]]; then
  echo "Dependency installer not found or not executable at $INSTALL_SCRIPT" >&2
  exit 1
fi

if [[ ! -x "$BUILD_SCRIPT" ]]; then
  echo "Build script not found or not executable at $BUILD_SCRIPT" >&2
  exit 1
fi

# Elevate to sudo for package installation if the user is not already root.
if [[ $(id -u) -ne 0 ]]; then
  echo "Running dependency installation with sudo..."
  sudo "$INSTALL_SCRIPT"
else
  "$INSTALL_SCRIPT"
fi

# Run the build and rely on the build script to fail if the APK is missing.
"$BUILD_SCRIPT"

if [[ -f "$APK_PATH" ]]; then
  apk_size_bytes=$(stat --format="%s" "$APK_PATH")
  apk_size_human=$(du -h "$APK_PATH" | cut -f1)
  echo "Build pipeline complete. APK located at: $APK_PATH"
  echo "APK size: ${apk_size_human} (${apk_size_bytes} bytes)"
else
  echo "Build pipeline completed but APK was not found at $APK_PATH" >&2
  exit 1
fi
