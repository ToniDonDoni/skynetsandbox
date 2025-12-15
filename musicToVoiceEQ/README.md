# Voice EQ Suggestion

## Task Description

This project automatically analyzes audio files and generates starting EQ settings for vocal tracks.

A Python script located in `src/voice_eq_analyzer.py`:
- reads audio files from the `data/` folder by default,
- analyzes their spectral content (optionally using vocal separation),
- computes recommended EQ parameters for vocals,
- saves the results in text and JSON format into the `artifacts/` folder.

This is not an attempt to recover the exact EQ used in a finished song. It provides a practical starting point for further manual adjustment.

---

## Usage

1. Ensure Python dependencies are available (tested with `librosa` and `numpy`).
2. Place music files to analyze in the `data/` directory.
3. Run the analyzer from the project root:

```bash
python src/voice_eq_analyzer.py  # defaults to scanning data/
```

You can also pass specific files or folders:

```bash
python src/voice_eq_analyzer.py data/theweekend.mp3 other_song.wav
```

Results are written to `artifacts/<song>_eq.txt` and `artifacts/<song>_eq.json`.
