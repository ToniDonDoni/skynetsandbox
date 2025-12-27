# Build Notes

## Current status
- The Unity Editor is not installed in this container, so the project cannot be built here. Attempting to run the editor CLI fails (`unity-editor` is not found).
- Android build support is required to produce `pupa.apk`.

## How to build `pupa.apk`
1. Install Unity **6000.3.2f1** with the Android Build Support modules (SDK/NDK & OpenJDK).
2. Open the project at `unity/first` in the Unity Hub/Editor to allow packages to restore.
3. From the Editor: `File -> Build Settings`, select **Android**, ensure XR settings are configured as expected, and click **Build**. Choose an output path named `pupa.apk`.
4. For a headless build, use a machine with the matching Unity version and run a command similar to:
   ```bash
   /path/to/Unity/Editor/Unity -batchmode -projectPath /absolute/path/to/unity/first \
     -buildTarget Android -executeMethod UnityEditor.BuildPipeline.BuildPlayer \
     -logFile unity_build.log -quit -nographics \
     -customBuildTarget Android -customBuildName pupa -customBuildPath /absolute/output/pupa.apk
   ```
5. After a successful build, commit only text assets (do not commit the generated `pupa.apk` or other binary artifacts).

## Troubleshooting
- Verify the installed editor version matches `6000.3.2f1` as listed in `ProjectSettings/ProjectVersion.txt`.
- Ensure Android SDK/NDK paths are configured in `Edit -> Preferences -> External Tools` if the editor cannot locate them.
- If using a CI runner, make sure the runner image includes the correct Unity + Android build modules or installs them before invoking the build.
