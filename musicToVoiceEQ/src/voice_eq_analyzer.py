"""Analyze music files to propose vocal EQ starting points."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import librosa
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"


@dataclass
class EqRecommendation:
    source: Path
    sample_rate: int
    low_cut_hz: float
    low_mid_dip_hz: float
    presence_boost_hz: float
    air_boost_hz: float
    de_esser_hz: float
    notes: List[str]

    def to_text(self) -> str:
        lines = [
            f"Source: {self.source.name}",
            f"Sample rate: {self.sample_rate} Hz",
            f"Low cut: {self.low_cut_hz:.0f} Hz (HPF)",
            f"Low-mid dip: {self.low_mid_dip_hz:.0f} Hz (to reduce mud)",
            f"Presence boost: {self.presence_boost_hz:.0f} Hz (clarity)",
            f"Air boost: {self.air_boost_hz:.0f} Hz (brightness)",
            f"De-esser target: {self.de_esser_hz:.0f} Hz",
            "Notes:",
            *(f"- {note}" for note in self.notes),
        ]
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({
            "source": self.source.name,
            "sample_rate": self.sample_rate,
            "low_cut_hz": self.low_cut_hz,
            "low_mid_dip_hz": self.low_mid_dip_hz,
            "presence_boost_hz": self.presence_boost_hz,
            "air_boost_hz": self.air_boost_hz,
            "de_esser_hz": self.de_esser_hz,
            "notes": self.notes,
        }, indent=2)


def load_audio(path: Path, target_sr: int = 44100, max_duration: float | None = 120.0) -> tuple[np.ndarray, int]:
    """Load mono audio with an optional duration cap for faster analysis."""
    y, sr = librosa.load(path, sr=target_sr, mono=True, duration=max_duration)
    return y, sr


def mean_spectrum(y: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    stft = librosa.stft(y, n_fft=2048, hop_length=512, window="hann")
    magnitude = np.abs(stft)
    mean_mag = magnitude.mean(axis=1)
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    return freqs, mean_mag


def find_energy_threshold_frequency(freqs: np.ndarray, magnitudes: np.ndarray, percentile: float) -> float:
    cumulative = np.cumsum(magnitudes)
    cutoff_idx = np.searchsorted(cumulative, cumulative[-1] * percentile)
    cutoff_idx = np.clip(cutoff_idx, 0, len(freqs) - 1)
    return float(freqs[cutoff_idx])


def dominant_band(freqs: np.ndarray, magnitudes: np.ndarray, min_hz: float, max_hz: float) -> float:
    band_mask = (freqs >= min_hz) & (freqs <= max_hz)
    if not np.any(band_mask):
        return float((min_hz + max_hz) / 2)
    band_freqs = freqs[band_mask]
    band_mags = magnitudes[band_mask]
    peak_idx = int(np.argmax(band_mags))
    return float(band_freqs[peak_idx])


def suggest_eq(y: np.ndarray, sr: int, source: Path) -> EqRecommendation:
    freqs, magnitudes = mean_spectrum(y, sr)
    low_cut = max(60.0, find_energy_threshold_frequency(freqs, magnitudes, 0.03))
    low_mid_dip = dominant_band(freqs, magnitudes, 150.0, 350.0)
    presence = dominant_band(freqs, magnitudes, 3000.0, 6000.0)
    air = dominant_band(freqs, magnitudes, 9000.0, 14000.0)
    de_esser = dominant_band(freqs, magnitudes, 4500.0, 9000.0)

    notes = [
        "Apply gentle high-pass filtering below the low-cut point.",
        "Tame the low-mid buildup if the vocal feels boxy.",
        "Boost presence for intelligibility; adjust Q to taste.",
        "Use a high-shelf for air; reduce if sibilance increases.",
        "De-esser center frequency targets the harshest band.",
    ]

    return EqRecommendation(
        source=source,
        sample_rate=sr,
        low_cut_hz=low_cut,
        low_mid_dip_hz=low_mid_dip,
        presence_boost_hz=presence,
        air_boost_hz=air,
        de_esser_hz=de_esser,
        notes=notes,
    )


def analyze_file(path: Path) -> EqRecommendation:
    audio, sr = load_audio(path)
    return suggest_eq(audio, sr, path)


def save_recommendation(rec: EqRecommendation, artifact_dir: Path) -> Path:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    txt_path = artifact_dir / f"{rec.source.stem}_eq.txt"
    json_path = artifact_dir / f"{rec.source.stem}_eq.json"

    txt_path.write_text(rec.to_text() + "\n")
    json_path.write_text(rec.to_json())
    return txt_path


def iter_audio_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_dir():
            yield from iter_audio_files(path.iterdir())
        elif path.suffix.lower() in {".wav", ".mp3", ".flac", ".m4a", ".ogg"}:
            yield path


def main(paths: list[str]) -> None:
    targets = [Path(p) for p in paths] if paths else [DATA_DIR]
    audio_files = list(iter_audio_files(targets))
    if not audio_files:
        raise SystemExit("No audio files found in the provided paths.")

    for audio_path in audio_files:
        rec = analyze_file(audio_path)
        save_recommendation(rec, ARTIFACTS_DIR)
        print(f"Saved EQ suggestion for {audio_path.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate vocal EQ starting points from music files.")
    parser.add_argument("paths", nargs="*", help="Audio file(s) or directories to analyze. Defaults to data/.")
    args = parser.parse_args()
    main(args.paths)
