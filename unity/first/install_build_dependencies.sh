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
  UNITY_KEY_URL="https://hub.unity3d.com/linux/keys/public"
  UNITY_KEYRING="/usr/share/keyrings/Unity_Technologies_ApS.gpg"
  tmp_key="$(mktemp)"
  trap 'rm -f "$tmp_key"' EXIT

  download_key() {
    local url="$1" dest="$2"
    if curl -fL --retry 5 --retry-all-errors --connect-timeout 10 --max-time 60 \
      -H "User-Agent: unity-key-fetcher" -o "$dest" "$url"; then
      return 0
    fi

    if command -v wget >/dev/null 2>&1; then
      wget -O "$dest" --retry-connrefused --waitretry=2 --tries=3 "$url"
    else
      return 1
    fi
  }

  if ! download_key "$UNITY_KEY_URL" "$tmp_key"; then
    echo "Warning: Failed to download Unity Hub signing key; skipping Unity Hub install." >&2
  elif ! gpg --dearmor <"$tmp_key" > "$UNITY_KEYRING"; then
    echo "Warning: Could not import Unity Hub signing key; skipping Unity Hub install." >&2
  else
    echo "deb [signed-by=$UNITY_KEYRING] https://hub.unity3d.com/linux/repos/deb stable main" \
      | tee /etc/apt/sources.list.d/unityhub.list

    if ! apt-get update; then
      echo "Warning: Failed to update apt after adding Unity Hub repo; skipping Unity Hub install." >&2
    else
      if ! apt-get install -y unityhub; then
        echo "Warning: Unity Hub install failed; continuing without it." >&2
      fi
    fi
  fi
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
