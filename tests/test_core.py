import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sentitriage.agent import ABSTAIN, PASS, QUEUE, decide  # noqa: E402
from sentitriage.calibration import (expected_calibration_error, fit_temperature,  # noqa: E402
                                     softmax)
from sentitriage.preprocess import normalize  # noqa: E402
from sentitriage.selective import aurc, choose_threshold, risk_coverage_curve  # noqa: E402


def test_normalize():
    out = normalize("Buenooooo @juan mira https://x.co 😍")
    assert "buenoo" in out.lower() and "ooo" not in out
    assert "@usuario" in out and "url" in out and "https" not in out
    assert "😍" not in out


def test_policy_actions():
    assert decide([0.9, 0.05, 0.05], tau=0.6).action == QUEUE
    assert decide([0.05, 0.05, 0.9], tau=0.6).action == PASS
    d = decide([0.4, 0.3, 0.3], tau=0.6)
    assert d.action == ABSTAIN and d.abstained and d.label == "negative"


def test_temperature_recovers_scale():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 3, 3000)
    true_logits = rng.normal(size=(3000, 3)); true_logits[np.arange(3000), y] += 1.5
    # sample labels from the true model, then present overconfident logits (x3)
    p = softmax(true_logits)
    y = np.array([rng.choice(3, p=pi) for pi in p])
    T = fit_temperature(true_logits * 3, y)
    assert 2.4 < T < 3.6
    assert expected_calibration_error(softmax(true_logits * 3, T), y) < \
        expected_calibration_error(softmax(true_logits * 3), y)


def test_risk_coverage_and_threshold():
    conf = np.array([0.9, 0.8, 0.7, 0.6, 0.5])
    correct = np.array([1, 1, 0, 1, 0])
    cov, risk, thr = risk_coverage_curve(conf, correct)
    assert cov[-1] == 1.0 and risk[0] == 0.0 and risk[-1] == pytest.approx(0.4)
    assert aurc(conf, correct) == pytest.approx(np.mean([0, 0, 1 / 3, 1 / 4, 2 / 5]))
    assert choose_threshold(conf, correct, 0.0) == 0.8
    assert choose_threshold(conf, correct, 0.3) == 0.6
