from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import librosa
import numpy as np


@dataclass(frozen=True)
class FrequencyBand:
    label: str
    low_hz: float
    high_hz: float


EqBand = tuple[str, int]


BAND_DEFINITIONS: Sequence[FrequencyBand] = (
    FrequencyBand("20–40", 20.0, 40.0),
    FrequencyBand("40–80", 40.0, 80.0),
    FrequencyBand("80–160", 80.0, 160.0),
    FrequencyBand("160–320", 160.0, 320.0),
    FrequencyBand("320–640", 320.0, 640.0),
    FrequencyBand("640–1,250", 640.0, 1250.0),
    FrequencyBand("1,250–2,500", 1250.0, 2500.0),
    FrequencyBand("2,500–5,000", 2500.0, 5000.0),
    FrequencyBand("5,000–10,000", 5000.0, 10000.0),
    FrequencyBand("10,000–20,000", 10000.0, 20000.0),
)


def _validate_bands(bands: Iterable[EqBand]) -> Sequence[EqBand]:
    validated = []
    for freq_range, level in bands:
        if not 1 <= level <= 10:
            raise ValueError(f"EQ level for {freq_range!r} must be between 1 and 10, got {level}.")
        validated.append((freq_range, level))
    return validated


def format_eq_table(bands: Iterable[EqBand]) -> str:
    """Format EQ band values as a two-column ASCII table."""

    validated_bands = _validate_bands(bands)

    freq_header = "Frequency (Hz)"
    level_header = "EQ Level (1–10)"

    freq_width = max(len(freq_header), *(len(freq) for freq, _ in validated_bands))
    level_width = max(len(level_header), *(len(str(level)) for _, level in validated_bands))

    def border() -> str:
        return f"+{'-' * (freq_width + 2)}+{'-' * (level_width + 2)}+"

    header = (
        border()
        + "\n"
        + f"| {freq_header.ljust(freq_width)} | {level_header.ljust(level_width)} |\n"
        + border()
    )

    rows = [f"| {freq.ljust(freq_width)} | {str(level).ljust(level_width)} |" for freq, level in validated_bands]

    return "\n".join([header, *rows, border()])


def write_eq_table(bands: Iterable[EqBand], output_path: Path) -> Path:
    """Write a formatted EQ table to the given output path."""

    table = format_eq_table(bands)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(table + "\n", encoding="utf-8")
    return output_path


def _band_energy(magnitude: np.ndarray, freqs: np.ndarray, band: FrequencyBand) -> float:
    mask = (freqs >= band.low_hz) & (freqs < band.high_hz)
    if not np.any(mask):
        return 0.0
    return float(np.mean(magnitude[mask]))


def _scale_to_levels(energies: np.ndarray) -> np.ndarray:
    eps = 1e-9
    db_values = librosa.amplitude_to_db(energies + eps, ref=np.max(energies) + eps)

    min_db = float(np.min(db_values))
    max_db = float(np.max(db_values))

    if max_db - min_db < 1e-6:
        return np.full_like(db_values, 5, dtype=int)

    scaled = np.interp(db_values, (min_db, max_db), (1.0, 10.0))
    return np.rint(scaled).astype(int)


def analyze_vocal_eq(
    audio_path: Path,
    bands: Sequence[FrequencyBand] = BAND_DEFINITIONS,
    sr: int = 44100,
    n_fft: int = 2048,
    hop_length: int = 512,
    duration: float | None = 90.0,
) -> list[EqBand]:
    """Analyze an audio file and suggest EQ levels for vocals."""

    y, sr = librosa.load(audio_path, sr=sr, mono=True, duration=duration)

    harmonic = librosa.effects.harmonic(y)
    stft = np.abs(librosa.stft(harmonic, n_fft=n_fft, hop_length=hop_length))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

    energies = np.array([_band_energy(stft, freqs, band) for band in bands])
    levels = _scale_to_levels(energies)

    return [(band.label, int(level)) for band, level in zip(bands, levels)]


def main() -> None:
    audio_file = Path("data/theweekend.mp3")
    output_file = Path("artifacts/eq_levels.txt")

    bands = analyze_vocal_eq(audio_file)
    write_eq_table(bands, output_file)
    print(f"Saved EQ table to {output_file}")


if __name__ == "__main__":
    main()
