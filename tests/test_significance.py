"""Unit tests for paired significance tests."""

import math

import numpy as np
import pytest

from rigor.stats.significance import paired_permutation_test, wilcoxon_signed_rank_test


# --- paired_permutation_test ---


def test_perm_identical_scores():
    scores = [0.5] * 50
    result = paired_permutation_test(scores, scores)
    assert result.p_value > 0.5


def test_perm_large_consistent_difference():
    a = [1.0] * 50
    b = [0.0] * 50
    result = paired_permutation_test(a, b)
    assert result.p_value < 0.001


def test_perm_small_noisy_difference():
    rng = np.random.default_rng(7)
    a = rng.normal(0.5, 0.3, 50).tolist()
    b = rng.normal(0.48, 0.3, 50).tolist()
    result = paired_permutation_test(a, b, random_seed=99)
    assert result.p_value > 0.05


def test_perm_unequal_length_raises():
    with pytest.raises(ValueError):
        paired_permutation_test([1.0, 2.0], [1.0])


def test_perm_nan_filtering():
    a = [1.0] * 50
    b = [0.0] * 50
    a[5] = float("nan")
    result = paired_permutation_test(a, b)
    assert result.n_pairs == 49
    assert result.p_value < 0.001


def test_perm_reproducibility():
    rng = np.random.default_rng(0)
    a = rng.random(50).tolist()
    b = rng.random(50).tolist()
    r1 = paired_permutation_test(a, b, random_seed=42)
    r2 = paired_permutation_test(a, b, random_seed=42)
    assert r1 == r2


# --- wilcoxon_signed_rank_test ---


def test_wilcoxon_identical_scores():
    scores = [0.5] * 50
    result = wilcoxon_signed_rank_test(scores, scores)
    # All zero diffs → wilcoxon fallback → p=1.0, n_pairs=0
    assert result.p_value >= 0.5


def test_wilcoxon_large_consistent_difference():
    a = [1.0] * 50
    b = [0.0] * 50
    result = wilcoxon_signed_rank_test(a, b)
    assert result.p_value < 0.001


def test_wilcoxon_small_noisy_difference():
    rng = np.random.default_rng(7)
    a = rng.normal(0.5, 0.3, 50).tolist()
    b = rng.normal(0.48, 0.3, 50).tolist()
    result = wilcoxon_signed_rank_test(a, b)
    assert result.p_value > 0.05


def test_wilcoxon_unequal_length_raises():
    with pytest.raises(ValueError):
        wilcoxon_signed_rank_test([1.0, 2.0], [1.0])


def test_wilcoxon_nan_filtering():
    a = [1.0] * 50
    b = [0.0] * 50
    a[5] = float("nan")
    result = wilcoxon_signed_rank_test(a, b)
    assert result.n_pairs == 49
    assert result.p_value < 0.001


def test_wilcoxon_reproducibility():
    """Wilcoxon is deterministic — same inputs always yield same result."""
    rng = np.random.default_rng(0)
    a = rng.random(50).tolist()
    b = rng.random(50).tolist()
    r1 = wilcoxon_signed_rank_test(a, b)
    r2 = wilcoxon_signed_rank_test(a, b)
    assert r1 == r2
