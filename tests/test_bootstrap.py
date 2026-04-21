import pytest

from rigor.stats.bootstrap import BootstrapCI, bootstrap_ci


def test_all_ones():
    result = bootstrap_ci([1.0] * 50)
    assert result.mean == pytest.approx(1.0, rel=1e-3)
    assert result.ci_low == pytest.approx(1.0, rel=1e-3)
    assert result.ci_high == pytest.approx(1.0, rel=1e-3)


def test_all_zeros():
    result = bootstrap_ci([0.0] * 50)
    assert result.mean == pytest.approx(0.0, abs=1e-9)
    assert result.ci_low == pytest.approx(0.0, abs=1e-9)
    assert result.ci_high == pytest.approx(0.0, abs=1e-9)


def test_balanced():
    scores = [1.0] * 25 + [0.0] * 25
    result = bootstrap_ci(scores, confidence=0.95, random_seed=42)
    assert result.mean == pytest.approx(0.5, rel=1e-3)
    assert result.ci_low < 0.5 < result.ci_high
    width = result.ci_high - result.ci_low
    assert 0.2 < width < 0.4


def test_single_sample():
    result = bootstrap_ci([0.75])
    assert result.mean == pytest.approx(0.75, rel=1e-3)
    assert result.ci_low == pytest.approx(0.75, rel=1e-3)
    assert result.ci_high == pytest.approx(0.75, rel=1e-3)


def test_empty_raises():
    with pytest.raises(ValueError):
        bootstrap_ci([])


def test_reproducibility():
    scores = [0.1, 0.5, 0.9, 0.3, 0.7] * 10
    r1 = bootstrap_ci(scores, random_seed=42)
    r2 = bootstrap_ci(scores, random_seed=42)
    assert r1 == r2
