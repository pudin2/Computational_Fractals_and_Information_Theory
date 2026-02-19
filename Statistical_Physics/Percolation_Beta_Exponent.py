import numpy as np
import matplotlib.pyplot as plt
from collections import deque


PC_SITE_SQUARE = 0.592746  


def burn_fraction(L: int, p: float, rng: np.random.Generator) -> float:

    forest = rng.random((L, L)) < p 
    total_trees = int(forest.sum())
    if total_trees == 0:
        return 0.0

    burned = np.zeros((L, L), dtype=bool)
    q = deque()

    left_col = forest[:, 0]
    rows = np.flatnonzero(left_col)
    for r in rows:
        burned[r, 0] = True
        q.append((r, 0))

    while q:
        r, c = q.popleft()

        if r > 0 and forest[r - 1, c] and not burned[r - 1, c]:
            burned[r - 1, c] = True
            q.append((r - 1, c))
        if r < L - 1 and forest[r + 1, c] and not burned[r + 1, c]:
            burned[r + 1, c] = True
            q.append((r + 1, c))
        if c > 0 and forest[r, c - 1] and not burned[r, c - 1]:
            burned[r, c - 1] = True
            q.append((r, c - 1))
        if c < L - 1 and forest[r, c + 1] and not burned[r, c + 1]:
            burned[r, c + 1] = True
            q.append((r, c + 1))

    burned_trees = int((burned & forest).sum())
    return burned_trees / total_trees


def estimate_beta_from_forest_fire(
    L_values=(40, 100, 200),
    p_values=None,
    trials=200,
    seed=7,
    pc=PC_SITE_SQUARE,
    fit_p_min=None,
    fit_p_max=None
):

    rng = np.random.default_rng(seed)

    if p_values is None:
        p_values = np.array([0.58, 0.59, 0.595, 0.60, 0.605, 0.61, 0.62, 0.64, 0.66])

    results = {}  

    for L in L_values:
        means = []
        stds = []
        for p in p_values:
            vals = [burn_fraction(L, float(p), rng) for _ in range(trials)]
            vals = np.array(vals, dtype=np.float64)
            means.append(vals.mean())
            stds.append(vals.std(ddof=1))
        results[L] = (p_values.copy(), np.array(means), np.array(stds))

    L_fit = max(L_values)
    p, Pmean, _ = results[L_fit]

    mask = p > pc
    if fit_p_min is not None:
        mask &= (p >= fit_p_min)
    if fit_p_max is not None:
        mask &= (p <= fit_p_max)

    mask &= (Pmean > 0)

    x = np.log(p[mask] - pc)
    y = np.log(Pmean[mask])

    beta, intercept = np.polyfit(x, y, 1)

    return results, beta, intercept, pc, L_fit


def plot_results(results, beta, intercept, pc, L_fit):
    plt.figure(figsize=(8, 5))
    for L, (p, meanP, stdP) in sorted(results.items()):
        plt.plot(p, meanP, marker="o", linewidth=1.5, label=f"L={L}")
    plt.axvline(pc, linestyle="--", linewidth=1.2, label=f"pc≈{pc:.3f}")
    plt.title("Forest fire / percolation: fraction of trees burned vs p")
    plt.xlabel("p (tree occupancy probability)")
    plt.ylabel("Fraction burned")
    plt.ylim(0, 1.02)
    plt.legend()
    plt.tight_layout()

    p, Pmean, _ = results[L_fit]
    mask = (p > pc) & (Pmean > 0)

    plt.figure(figsize=(7, 5))
    xx = np.log(p[mask] - pc)
    yy = np.log(Pmean[mask])
    plt.plot(xx, yy, "o", label=f"data (L={L_fit})")

    xline = np.linspace(xx.min(), xx.max(), 100)
    yline = beta * xline + intercept
    plt.plot(xline, yline, "-", label=f"fit slope β≈{beta:.4f}")

    plt.title("Power-law evidence: log P(p) vs log(p - pc)")
    plt.xlabel("log(p - pc)")
    plt.ylabel("log(P(p))")
    plt.legend()
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":

    results, beta, intercept, pc, L_fit = estimate_beta_from_forest_fire(
        L_values=(40, 100, 200),
        p_values=np.array([0.585, 0.59, 0.595, 0.60, 0.605, 0.61, 0.62, 0.64]),
        trials=200,
        seed=7,
        pc=PC_SITE_SQUARE,
    )

    print(f"Using L={L_fit} for beta fit")
    print(f"Estimated beta: {beta:.6f}")
    print(f"Theoretical beta = 5/36 ≈ {5/36:.6f}")

    plot_results(results, beta, intercept, pc, L_fit)
