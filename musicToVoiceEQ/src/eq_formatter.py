from __future__ import annotations

"""Compute vocal-focused EQ suggestions as per-band dB boosts or cuts.

The script estimates how loudly each vocal-related band speaks inside the mix
by isolating the stable (harmonic) parts of the track and comparing their
relative strength. Gains are centered so the output simply says "boost the
bands that trail the average, trim the ones that dominate", producing a few
decibel nudges to help the voice sit as it already does in the song.
"""

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


BandGain = tuple[FrequencyBand, float]


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


def _band_energy(magnitude: np.ndarray, freqs: np.ndarray, band: FrequencyBand) -> float:
    mask = (freqs >= band.low_hz) & (freqs < band.high_hz)
    if not np.any(mask):
        return 0.0
    return float(np.mean(magnitude[mask]))


def _band_profile_db(energies: np.ndarray) -> np.ndarray:
    """Return centered band levels in dB without rounding."""

    eps = 1e-9
    db_values = librosa.amplitude_to_db(energies + eps, ref=np.max(energies) + eps)

    if np.ptp(db_values) < 1e-6:
        return np.zeros_like(db_values)

    return db_values - float(np.mean(db_values))


def _band_gains_db(energies: np.ndarray) -> np.ndarray:
    """Return centered, rounded dB offsets derived from band energies."""

    centered = _band_profile_db(energies)
    clipped = np.clip(centered, -9.0, 9.0)
    return np.rint(clipped)


def _format_freq_range(band: FrequencyBand) -> str:
    if band.low_hz >= 1000 and band.high_hz >= 1000:
        low = band.low_hz / 1000
        high = band.high_hz / 1000
        return f"{low:g}–{high:g} kHz"
    return f"{band.low_hz:g}–{band.high_hz:g} Hz"


def format_eq_adjustments(adjustments: Iterable[BandGain]) -> str:
    """Format EQ suggestions as +/- dB lines with frequency ranges."""

    lines = [
        f"{gain:+.0f} dB @ {_format_freq_range(band)}" for band, gain in adjustments
    ]
    return "\n".join(lines)


def write_eq_adjustments(adjustments: Iterable[BandGain], output_path: Path) -> Path:
    """Write formatted EQ adjustments to the given output path."""

    output = format_eq_adjustments(adjustments)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output + "\n", encoding="utf-8")
    return output_path


def _band_energies(
    audio_path: Path,
    bands: Sequence[FrequencyBand],
    sr: int,
    n_fft: int,
    hop_length: int,
    duration: float | None,
) -> np.ndarray:
    """Compute average magnitude per band for an audio file."""

    y, sr = librosa.load(audio_path, sr=sr, mono=True, duration=duration)
    harmonic = librosa.effects.harmonic(y)
    stft = np.abs(librosa.stft(harmonic, n_fft=n_fft, hop_length=hop_length))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

    return np.array([_band_energy(stft, freqs, band) for band in bands])


def analyze_vocal_eq(
    audio_path: Path,
    bands: Sequence[FrequencyBand] = BAND_DEFINITIONS,
    sr: int = 44100,
    n_fft: int = 2048,
    hop_length: int = 512,
    duration: float | None = 90.0,
) -> list[BandGain]:
    """Analyze an audio file and suggest EQ gains for vocals."""

    energies = _band_energies(audio_path, bands, sr, n_fft, hop_length, duration)
    gains_db = _band_gains_db(energies)

    return [(band, float(gain)) for band, gain in zip(bands, gains_db)]


def analyze_matching_vocal_eq(
    reference_path: Path,
    target_path: Path,
    bands: Sequence[FrequencyBand] = BAND_DEFINITIONS,
    sr: int = 44100,
    n_fft: int = 2048,
    hop_length: int = 512,
    duration: float | None = 90.0,
) -> list[BandGain]:
    """Suggest EQ gains that align the target vocals with the reference track."""

    reference_energies = _band_energies(
        reference_path, bands, sr, n_fft, hop_length, duration
    )
    target_energies = _band_energies(target_path, bands, sr, n_fft, hop_length, duration)

    reference_profile = _band_profile_db(reference_energies)
    target_profile = _band_profile_db(target_energies)

    # EQ values are derived by subtracting the target's centered band levels
    # from the reference profile: positive numbers indicate where the target
    # should be boosted to match the reference vocal presence, and negative
    # numbers mark bands to trim.
    adjustments = reference_profile - target_profile
    adjustments = np.clip(np.rint(adjustments), -9.0, 9.0)

    return [(band, float(gain)) for band, gain in zip(bands, adjustments)]


def main() -> None:
    reference_file = Path("data/1/reference/theweekend.mp3")
    target_file = Path("data/1/target/zvezda.wav")
    output_file = Path("artifacts/target_to_reference_eq.txt")

    bands = analyze_matching_vocal_eq(reference_file, target_file)
    write_eq_adjustments(bands, output_file)
    print(
        "Saved EQ adjustments for aligning target vocals to reference: "
        f"{output_file}"
    )


if __name__ == "__main__":
    main()
