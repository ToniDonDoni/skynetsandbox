# Voice EQ Suggestion

## Task Description

This project is designed to automatically analyze audio files and generate starting EQ settings for vocal tracks.

A Python script located in the src/ directory:
- reads a *reference* and *target* audio file from the `data/1` folder (by default the first 90 seconds of `data/1/reference/theweekend.mp3` and `data/1/target/zvezda.wav`),
- separates the harmonic (vocal-focused) content,
- measures its spectral energy across vocal-relevant bands,
- computes recommended EQ parameters for vocals and for matching the target to the reference,
- saves the results in text format into the artifacts/ folder.

This is not an attempt to recover the exact EQ used in a finished song.
It provides a practical starting point for further manual adjustment based on the recorded voice in the supplied mix.

---

## Output format

The EQ suggestions are written as one line per band using decibel changes and
a frequency range, e.g.:

```
-3 dB @ 250–350 Hz
+2 dB @ 3–5 kHz
```

Positive numbers indicate a boost, negative numbers a cut. The matching
workflow writes the adjustments that make the target resemble the reference
into `artifacts/target_to_reference_eq.txt`.

---

## How EQ levels are computed

1. Load up to 90 seconds from the chosen reference and target files (update the paths in `main` to use other tracks).
2. Use harmonic-percussive separation (`librosa.effects.harmonic`) to emphasize steady, vocal-like components.
3. Compute an STFT magnitude spectrogram and aggregate the average amplitude inside ten fixed vocal bands (20–20,000 Hz).
4. Convert band amplitudes to decibels relative to the strongest band, center them around the average band energy, and round to whole-number boosts/cuts in dB.
5. Subtract the target's centered profile from the reference profile to see which bands need boosts or cuts to match the reference vocal presence.

### How the script focuses on the "vocal" part of the mix

The script narrows in on vocal-related energy in two ways:

- **Harmonic isolation:** `librosa.effects.harmonic` filters out most percussive elements so the subsequent analysis is dominated by sustained tones (a good proxy for sung or spoken vocals).
- **Band choice:** the ten bands include the core vocal intelligibility region (roughly 160 Hz–5 kHz), plus flanking ranges that capture chest weight below and brightness/air above. You can tighten the focus to the most vocal-centric bands by adjusting `BAND_DEFINITIONS` in `src/eq_formatter.py` (for example, using only 160–5,000 Hz bands).

---

## Running the analysis

```bash
pip install -r requirements.txt  # installs librosa and numpy
python src/eq_formatter.py
```

The script will analyze the bundled sample track and overwrite `artifacts/eq_levels.txt` with the computed EQ table.
