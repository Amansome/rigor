from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BootstrapCI:
    mean: float
    ci_low: float
    ci_high: float
    n_samples: int
    confidence: float
    n_iterations: int


def bootstrap_ci(
    scores: list[float],
    confidence: float = 0.95,
    n_iterations: int = 10_000,
    random_seed: int | None = 42,
) -> BootstrapCI:
    """
    Compute a percentile-based bootstrap confidence interval on the mean of `scores`.

    Resampling is with replacement, same size as the input. For each resample we compute
    the mean, then take the empirical quantiles at (1-confidence)/2 and 1-(1-confidence)/2
    as the CI bounds.

    random_seed is used to make results reproducible in tests. Pass None for
    nondeterministic sampling.
    """
    if len(scores) == 0:
        raise ValueError("scores must not be empty")

    arr = np.array(scores, dtype=float)
    n = len(arr)
    mean = float(arr.mean())

    if n == 1:
        return BootstrapCI(
            mean=mean,
            ci_low=mean,
            ci_high=mean,
            n_samples=n,
            confidence=confidence,
            n_iterations=n_iterations,
        )

    rng = np.random.default_rng(random_seed)
    # Vectorized: draw (n_iterations, n) indices with replacement, compute means
    indices = rng.integers(0, n, size=(n_iterations, n))
    boot_means = arr[indices].mean(axis=1)

    alpha = (1.0 - confidence) / 2.0
    ci_low = float(np.quantile(boot_means, alpha))
    ci_high = float(np.quantile(boot_means, 1.0 - alpha))

    return BootstrapCI(
        mean=mean,
        ci_low=ci_low,
        ci_high=ci_high,
        n_samples=n,
        confidence=confidence,
        n_iterations=n_iterations,
    )
