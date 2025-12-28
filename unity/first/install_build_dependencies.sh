#!/usr/bin/env bash
# Install system dependencies and (optionally) Unity Editor + Android support.
# This installs runtime libraries and tooling Unity depends on, configures the
# Unity Hub apt repository, installs Unity Hub, and installs the Unity Editor
# version requested via UNITY_INSTALL_VERSION (default: 6000.3.2f1).
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
UNITY_INSTALL_VERSION="${UNITY_INSTALL_VERSION:-6000.3.2f1}"
UNITY_SKIP_EDITOR_INSTALL="${UNITY_SKIP_EDITOR_INSTALL:-0}"
UNITY_INSTALL_USER="${SUDO_USER:-${USER:-root}}"
UNITY_INSTALL_HOME="$(getent passwd "$UNITY_INSTALL_USER" 2>/dev/null | cut -d: -f6 || echo "$HOME")"

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

unity_bin_path() {
  local search_root="$1" version="$2"
  find "$search_root" -type f -path "*/Hub/Editor/${version}/Editor/Unity*" -executable -print -quit
}

install_unity_editor() {
  if [[ "$UNITY_SKIP_EDITOR_INSTALL" == "1" ]]; then
    echo "UNITY_SKIP_EDITOR_INSTALL=1 set; skipping Unity Editor install."
    return
  fi

  local existing_bin
  existing_bin="$(unity_bin_path "$UNITY_INSTALL_HOME" "$UNITY_INSTALL_VERSION" || true)"
  if [[ -n "$existing_bin" ]]; then
    echo "Unity $UNITY_INSTALL_VERSION already present at $existing_bin; skipping install."
    return
  fi

  echo "Installing Unity $UNITY_INSTALL_VERSION for user $UNITY_INSTALL_USER (HOME=$UNITY_INSTALL_HOME)..."

  if [[ "$UNITY_INSTALL_USER" == "root" ]]; then
    xvfb-run -a unityhub -- --headless install --version "$UNITY_INSTALL_VERSION"
  else
    sudo -u "$UNITY_INSTALL_USER" HOME="$UNITY_INSTALL_HOME" \
      xvfb-run -a unityhub -- --headless install --version "$UNITY_INSTALL_VERSION"
  fi

  local unity_bin
  unity_bin="$(unity_bin_path "$UNITY_INSTALL_HOME" "$UNITY_INSTALL_VERSION" || true)"
  if [[ -z "$unity_bin" ]]; then
    echo "Unity binary not found after install of $UNITY_INSTALL_VERSION" >&2
    exit 1
  fi

  echo "Unity installed at $unity_bin"
  cat > /tmp/unity-path <<EOF
UNITY_PATH="$unity_bin"
UNITY_VERSION="$UNITY_INSTALL_VERSION"
EOF
  chmod 0644 /tmp/unity-path || true
}

install_unity_editor

cat <<MSG
System dependencies (including Xvfb for headless installs) installed.
Unity install target: $UNITY_INSTALL_VERSION
Unity install user:   $UNITY_INSTALL_USER
Unity home:           $UNITY_INSTALL_HOME
If UNITY_SKIP_EDITOR_INSTALL=1, the editor install step was skipped.
If /tmp/unity-path exists, it contains UNITY_PATH/UNITY_VERSION you can append to your env.
MSG
