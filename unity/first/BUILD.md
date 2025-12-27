# Build Notes

## Current status
- The Unity Editor is not installed in this container, so the project cannot be built here. Attempting to run the editor CLI fails (`unity-editor` is not found).
- Android build support is required to produce `pupa.apk`.

## How to build `pupa.apk`
1. Run `sudo ./install_build_dependencies.sh` to install the Linux runtime and tooling Unity depends on (GTK, OpenJDK, etc.).
2. Install Unity **6000.3.2f1** with the Android Build Support modules (SDK/NDK & OpenJDK).
2. Open the project at `unity/first` in the Unity Hub/Editor to allow packages to restore.
3. From the Editor: `File -> Build Settings`, select **Android**, ensure XR settings are configured as expected, and click **Build**. Choose an output path named `pupa.apk` (for example: `Builds/Android/pupa.apk`).
4. For a headless build, use a machine with the matching Unity version and run a command similar to:
   ```bash
   /path/to/Unity/Editor/Unity -batchmode -projectPath /absolute/path/to/unity/first \
     -buildTarget Android -executeMethod UnityEditor.BuildPipeline.BuildPlayer \
     -logFile unity_build.log -quit -nographics \
     -customBuildTarget Android -customBuildName pupa -customBuildPath /absolute/output/Builds/Android/pupa.apk
   ```
5. After a successful build, confirm that `Builds/Android/pupa.apk` exists and runs on the target headset/emulator, then commit only text assets (do not commit the generated `pupa.apk` or other binary artifacts).

## Automated build helper
- Before building, install runtime/tooling dependencies via `sudo ./install_build_dependencies.sh` on Debian/Ubuntu-based systems (or run the combined `./run_build_pipeline.sh`).
- If you prefer a repeatable command, create (or run) a helper script such as `./build_android.sh` with contents similar to:
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  UNITY_PATH="/path/to/Unity/Editor/Unity"
  PROJECT_PATH="$(pwd)"
  OUTPUT_PATH="$PROJECT_PATH/Builds/Android/pupa.apk"
  mkdir -p "$(dirname "$OUTPUT_PATH")"
  "$UNITY_PATH" -batchmode -nographics -projectPath "$PROJECT_PATH" \
    -buildTarget Android -executeMethod UnityEditor.BuildPipeline.BuildPlayer \
    -logFile "$PROJECT_PATH/unity_build.log" -quit \
    -customBuildTarget Android -customBuildName pupa -customBuildPath "$OUTPUT_PATH"
  echo "APK written to $OUTPUT_PATH"
  ```
- Ensure execute permission (`chmod +x build_android.sh`) and run the script from the `unity/first` directory once Unity + Android modules are installed.

## Quick test flow
1. `./run_build_pipeline.sh` — installs prerequisites (with sudo if needed), runs the headless Android build, confirms `Builds/Android/pupa.apk` exists, and prints the APK size.
2. If you prefer manual steps: `sudo ./install_build_dependencies.sh`, then `UNITY_PATH="/path/to/Unity/Editor/Unity" ./build_android.sh`; after completion, verify `Builds/Android/pupa.apk` exists and note its reported size.

## CI build (GitHub Actions)
- Workflow: `.github/workflows/build-android-apk.yml` (runs on pushes/PRs to `main` and manually via **Run workflow**).
- Requirements: set `UNITY_LICENSE` in the repo secrets so GameCI can activate Unity 6000.3.2f1 with Android modules.
- What it does: checks out the repo, runs `game-ci/unity-builder@v4` against `unity/first`, produces `Builds/Android/pupa.apk`, verifies the file exists/prints its size, and uploads the APK as an artifact. The job fails if the APK is missing.

## Troubleshooting
- Verify the installed editor version matches `6000.3.2f1` as listed in `ProjectSettings/ProjectVersion.txt`.
- Ensure Android SDK/NDK paths are configured in `Edit -> Preferences -> External Tools` if the editor cannot locate them.
- If using a CI runner, make sure the runner image includes the correct Unity + Android build modules or installs them before invoking the build.

## Latest container attempt
- Attempting to invoke the Unity CLI (`unity-editor -batchmode ...`) in this container fails because the editor is not installed, so no `pupa.apk` could be produced here. Run the build on a machine that has Unity 6000.3.2f1 with Android Build Support.
- Because the APK is not produced in this environment, there is no file size to report. Once you build on a machine with Unity installed, the helper scripts will print the size (or you can run `stat -c "%n: %s bytes" Builds/Android/pupa.apk`).
