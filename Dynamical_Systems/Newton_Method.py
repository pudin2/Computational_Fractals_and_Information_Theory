import numpy as np
import matplotlib.pyplot as plt


def newton_sin(x0, tol=1e-12, max_iter=50):
    x = x0
    for k in range(max_iter):
        c = np.cos(x)
        if abs(c) < 1e-14:  
            return np.nan, k, False
        x_next = x - np.tan(x)
        if abs(x_next - x) < tol:
            return x_next, k + 1, True
        x = x_next
    return x, max_iter, False


N = 4000
xs = np.linspace(0, np.pi, N)
iters = np.zeros(N, dtype=float)
root_id = np.full(N, np.nan)  

for i, x0 in enumerate(xs):
    x, k, ok = newton_sin(x0)
    iters[i] = k if ok else np.nan
    if ok:

        if abs(x - 0) < abs(x - np.pi):
            root_id[i] = 0
        else:
            root_id[i] = 1

plt.figure()
mask0 = root_id == 0
mask1 = root_id == 1

plt.scatter(xs[mask0], iters[mask0], s=2, label="Converge to 0")
plt.scatter(xs[mask1], iters[mask1], s=2, label="Converge to pi")

plt.axvline(np.pi/2, linestyle="--")
plt.xlabel("x0")
plt.ylabel("Iterations Until Convergence")
plt.title("Newton Method for sin(x)=0 in [0, pi]")
plt.legend()
plt.show()
