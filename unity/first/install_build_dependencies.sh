#!/usr/bin/env bash
# Install system dependencies needed to run Unity headless Android builds.
# This script installs runtime libraries and tooling that Unity depends on;
# it also configures the Unity Hub apt repository and installs Unity Hub so you
# can install Unity 6000.3.2f1 with Android Build Support afterward.
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
  libgtk-3-0t64 libnss3 libasound2t64 libxrandr2 libxrender1 libxtst6 libxi6 libglu1-mesa
  xvfb
)
ANDROID_TOOLING=(
  openjdk-17-jdk unzip ca-certificates curl
)

apt-get update
apt-get install -y "${RUNTIME_PACKAGES[@]}" "${ANDROID_TOOLING[@]}"

if [[ "${UNITY_SKIP_UNITYHUB_INSTALL:-0}" == "1" ]]; then
  echo "UNITY_SKIP_UNITYHUB_INSTALL=1 set; skipping Unity Hub install."
elif ! command -v unityhub >/dev/null 2>&1; then
  echo "Adding Unity Hub repository and installing unityhub..."
  if ! curl -fsSL https://hub.unity3d.com/linux/keys/public | gpg --dearmor > /usr/share/keyrings/Unity_Technologies_ApS.gpg; then
    echo "Failed to download Unity Hub signing key; check network access and try again." >&2
    exit 1
  fi

  echo "deb [signed-by=/usr/share/keyrings/Unity_Technologies_ApS.gpg] https://hub.unity3d.com/linux/repos/deb stable main" \
    | tee /etc/apt/sources.list.d/unityhub.list

  apt-get update
  apt-get install -y unityhub
else
  echo "Unity Hub already installed; skipping repository setup."
fi

cat <<'MSG'
System dependencies (including Xvfb for headless installs) installed.
Next steps:
1) Use Unity Hub to install Unity 6000.3.2f1 with the Android Build Support modules (SDK/NDK + OpenJDK).
2) Export the Unity executable path via UNITY_PATH if it is not on PATH.
3) Run ./build_android.sh to produce Builds/Android/pupa.apk.
MSG
