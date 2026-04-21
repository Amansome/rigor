"""Paired significance tests for comparing two eval runs."""

import math
from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class PairedTestResult:
    test_name: str
    n_pairs: int
    mean_difference: float
    p_value: float
    significant_at_0_05: bool


def _filter_pairs(
    scores_a: list[float], scores_b: list[float]
) -> tuple[np.ndarray, np.ndarray]:
    if len(scores_a) != len(scores_b):
        raise ValueError(
            f"scores_a and scores_b must have equal length, got {len(scores_a)} and {len(scores_b)}"
        )
    pairs = [
        (a, b)
        for a, b in zip(scores_a, scores_b)
        if a is not None
        and b is not None
        and not (isinstance(a, float) and math.isnan(a))
        and not (isinstance(b, float) and math.isnan(b))
    ]
    if len(pairs) < 2:
        raise ValueError("Not enough paired observations")
    a_arr = np.array([p[0] for p in pairs], dtype=float)
    b_arr = np.array([p[1] for p in pairs], dtype=float)
    return a_arr, b_arr


def paired_permutation_test(
    scores_a: list[float],
    scores_b: list[float],
    n_iterations: int = 10_000,
    random_seed: int | None = 42,
) -> PairedTestResult:
    """
    Two-sided paired permutation test on the mean difference.

    For each iteration we independently flip each pair with probability 0.5 and
    compute the mean difference. The p-value is the fraction of permuted
    differences whose absolute value is >= the observed absolute mean difference.
    """
    a_arr, b_arr = _filter_pairs(scores_a, scores_b)
    n = len(a_arr)
    observed_diff = float(np.mean(a_arr) - np.mean(b_arr))

    rng = np.random.default_rng(random_seed)
    # Shape (n_iterations, n): each cell is +1 or -1
    signs = rng.choice([-1.0, 1.0], size=(n_iterations, n))
    diffs = a_arr - b_arr  # shape (n,)
    permuted_means = (signs * diffs).mean(axis=1)  # shape (n_iterations,)
    p_value = float(np.mean(np.abs(permuted_means) >= abs(observed_diff)))

    return PairedTestResult(
        test_name="paired_permutation",
        n_pairs=n,
        mean_difference=observed_diff,
        p_value=p_value,
        significant_at_0_05=p_value < 0.05,
    )


def wilcoxon_signed_rank_test(
    scores_a: list[float],
    scores_b: list[float],
) -> PairedTestResult:
    """
    Wilcoxon signed-rank test via scipy.stats.wilcoxon. Two-sided. Drops zero-diff
    pairs (scipy's default zero_method='wilcox').
    """
    a_arr, b_arr = _filter_pairs(scores_a, scores_b)
    n = len(a_arr)
    mean_diff = float(np.mean(a_arr) - np.mean(b_arr))

    try:
        result = stats.wilcoxon(a_arr, b_arr, alternative="two-sided")
        p_value = float(result.pvalue)
    except ValueError:
        p_value = float("nan")

    if math.isnan(p_value):
        # All differences are zero — no non-zero pairs
        return PairedTestResult(
            test_name="wilcoxon_signed_rank",
            n_pairs=0,
            mean_difference=mean_diff,
            p_value=1.0,
            significant_at_0_05=False,
        )

    return PairedTestResult(
        test_name="wilcoxon_signed_rank",
        n_pairs=n,
        mean_difference=mean_diff,
        p_value=p_value,
        significant_at_0_05=p_value < 0.05,
    )
