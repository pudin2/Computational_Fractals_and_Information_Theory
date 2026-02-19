import numpy as np
import matplotlib.pyplot as plt

def newton_fractal(f, fp, roots, xlim=(-2,2), ylim=(-2,2), res=800, max_iter=50, tol=1e-6):

    re = np.linspace(xlim[0], xlim[1], res)
    im = np.linspace(ylim[0], ylim[1], res)
    Z = re[None, :] + 1j * im[:, None]

    root_index = -np.ones(Z.shape, dtype=int)
    iters = np.zeros(Z.shape, dtype=int)
    active = np.ones(Z.shape, dtype=bool)

    for k in range(max_iter):
        Z_active = Z[active]
        fz = f(Z_active)
        fpz = fp(Z_active)

        safe = np.abs(fpz) > 1e-14
        Z_new = Z_active.copy()
        Z_new[safe] = Z_active[safe] - fz[safe] / fpz[safe]
        Z[active] = Z_new

        for r_i, r in enumerate(roots):
            conv = active & (np.abs(Z - r) < tol) & (root_index == -1)
            root_index[conv] = r_i
            iters[conv] = k + 1

        active = active & (root_index == -1)

        if not active.any():
            break

    return root_index, iters

f  = lambda z: z**3 - 1
fp = lambda z: 3*z**2
roots = [1+0j,
         np.exp(2j*np.pi/3),
         np.exp(4j*np.pi/3)]

root_index, iters = newton_fractal(
    f, fp, roots,
    xlim=(-2,2), ylim=(-2,2),
    res=900, max_iter=40, tol=1e-6
)

plt.figure()
plt.imshow(root_index, origin="lower", extent=(-2,2,-2,2))
plt.title("Basins ")
plt.xlabel("Re(z)")
plt.ylabel("Im(z)")
plt.show()

plt.figure()
plt.imshow(iters, origin="lower", extent=(-2,2,-2,2))
plt.title("Iterations Until Convergence")
plt.xlabel("Re(z)")
plt.ylabel("Im(z)")
plt.show()
