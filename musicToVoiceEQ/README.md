# Voice EQ Suggestion

## Task Description

This project is designed to automatically analyze audio files and generate starting EQ settings for vocal tracks.

A Python script located in the src/ directory:
- reads audio files from the data/ folder (by default the first 90 seconds of `data/theweekend.mp3`),
- separates the harmonic (vocal-focused) content,
- measures its spectral energy across vocal-relevant bands,
- computes recommended EQ parameters for vocals,
- saves the results in text format into the artifacts/ folder.

This is not an attempt to recover the exact EQ used in a finished song.
It provides a practical starting point for further manual adjustment based on the recorded voice in the supplied mix.

---

## Output format

The EQ suggestions are written as a two-column ASCII table where the first column
contains the frequency range in Hz and the second column contains the EQ level
from **1** (cut) to **10** (boost) for that range. Example:

```
+----------------+-----------------+
| Frequency (Hz) | EQ Level (1–10) |
+----------------+-----------------+
| 20–40          | 2               |
| 40–80          | 3               |
| 80–160         | 4               |
| 160–320        | 5               |
| 320–640        | 4               |
| 640–1,250      | 5               |
| 1,250–2,500    | 6               |
| 2,500–5,000    | 7               |
| 5,000–10,000   | 8               |
| 10,000–20,000  | 9               |
+----------------+-----------------+
```

The default script writes the table to `artifacts/eq_levels.txt`.

---

## How EQ levels are computed

1. Load up to 90 seconds from `data/theweekend.mp3` (or another file if you change the path in `main`).
2. Use harmonic-percussive separation (`librosa.effects.harmonic`) to emphasize steady, vocal-like components.
3. Compute an STFT magnitude spectrogram and aggregate the average amplitude inside ten fixed vocal bands (20–20,000 Hz).
4. Convert band amplitudes to decibels relative to the strongest band and scale the values into the **1–10** range so that louder vocal bands receive higher EQ levels.

---

## Running the analysis

```bash
pip install -r requirements.txt  # installs librosa and numpy
python src/eq_formatter.py
```

The script will analyze the bundled sample track and overwrite `artifacts/eq_levels.txt` with the computed EQ table.
