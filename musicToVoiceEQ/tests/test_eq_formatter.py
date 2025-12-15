import sys
from pathlib import Path

import numpy as np
import pytest

# Allow importing the script from the src directory without installing as a package
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from eq_formatter import (  # noqa: E402
    BAND_DEFINITIONS,
    analyze_matching_vocal_eq,
    write_eq_adjustments,
)


@pytest.mark.slow
def test_matching_analysis_generates_artifact(tmp_path: Path) -> None:
    reference = PROJECT_ROOT / "data/1/reference/theweekend.mp3"
    target = PROJECT_ROOT / "data/1/target/zvezda.wav"

    # Limit duration to keep CI runtime manageable while still exercising analysis.
    adjustments = analyze_matching_vocal_eq(reference, target, duration=10.0)

    assert len(adjustments) == len(BAND_DEFINITIONS)
    gains = np.array([gain for _, gain in adjustments], dtype=float)
    assert np.all(np.isfinite(gains))

    output_path = tmp_path / "target_to_reference_eq.txt"
    written = write_eq_adjustments(adjustments, output_path)

    assert written.exists(), "EQ artifact was not created"
    lines = written.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == len(BAND_DEFINITIONS)
    assert all(line.startswith(("+", "-")) and " dB @ " in line for line in lines)
