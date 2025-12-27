#!/usr/bin/env bash
# Install system dependencies needed to run Unity headless Android builds.
# This script installs runtime libraries and tooling that Unity depends on;
# you must still install Unity 6000.3.2f1 with Android Build Support separately.
set -euo pipefail

if [[ $(id -u) -ne 0 ]]; then
  echo "Please run this script with sudo so packages can be installed." >&2
  exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This installer currently supports Debian/Ubuntu systems with apt-get." >&2
  exit 1
fi

# Packages commonly required by the Unity Editor and Android builds on Linux.
RUNTIME_PACKAGES=(
  libgtk-3-0 libnss3 libasound2 libxrandr2 libxrender1 libxtst6 libxi6 libglu1-mesa
)
ANDROID_TOOLING=(
  openjdk-17-jdk unzip ca-certificates curl
)

apt-get update
apt-get install -y "${RUNTIME_PACKAGES[@]}" "${ANDROID_TOOLING[@]}"

cat <<'MSG'
System dependencies installed.
Next steps:
1) Install Unity 6000.3.2f1 with the Android Build Support modules (SDK/NDK + OpenJDK).
2) Export the Unity executable path via UNITY_PATH if it is not on PATH.
3) Run ./build_android.sh to produce Builds/Android/pupa.apk.
MSG
