import numpy as np
import matplotlib.pyplot as plt


def diamond_square(n_power=9, roughness=0.62, seed=7):
    rng = np.random.default_rng(seed)
    size = 2**n_power + 1
    Z = np.zeros((size, size), dtype=np.float32)

    Z[0, 0] = rng.random()
    Z[0, -1] = rng.random()
    Z[-1, 0] = rng.random()
    Z[-1, -1] = rng.random()

    step = size - 1
    scale = 1.0

    while step > 1:
        half = step // 2

        for y in range(half, size - 1, step):
            for x in range(half, size - 1, step):
                a = Z[y - half, x - half]
                b = Z[y - half, x + half]
                c = Z[y + half, x - half]
                d = Z[y + half, x + half]
                Z[y, x] = (a + b + c + d) / 4.0 + rng.normal(0, scale)

        for y in range(0, size, half):
            for x in range((y + half) % step, size, step):
                vals = []
                if y - half >= 0: vals.append(Z[y - half, x])
                if y + half < size: vals.append(Z[y + half, x])
                if x - half >= 0: vals.append(Z[y, x - half])
                if x + half < size: vals.append(Z[y, x + half])
                Z[y, x] = np.mean(vals) + rng.normal(0, scale)

        step = half
        scale *= roughness

    Z -= Z.min()
    Z /= (Z.max() + 1e-12)
    return Z


def smooth_cheap(Z, passes=2):
    Zs = Z.copy()
    for _ in range(passes):
        Zs = (
            0.5 * Zs
            + 0.125 * (np.roll(Zs, 1, 0) + np.roll(Zs, -1, 0) + np.roll(Zs, 1, 1) + np.roll(Zs, -1, 1))
        )
    Zs -= Zs.min()
    Zs /= (Zs.max() + 1e-12)
    return Zs


def plot_colored_3d(Z):
    n = Z.shape[0]
    x = np.linspace(0, 1, n)
    y = np.linspace(0, 1, n)
    X, Y = np.meshgrid(x, y)

    fig = plt.figure(figsize=(8, 6))
    ax3d = fig.add_subplot(1, 1, 1, projection="3d")

    surf = ax3d.plot_surface(
        X, Y, Z,
        cmap="terrain",      
        linewidth=0,
        antialiased=True
    )

    ax3d.view_init(elev=25, azim=-60)
    ax3d.set_xticks([])
    ax3d.set_yticks([])
    ax3d.set_zticks([])
    ax3d.set_box_aspect((1, 1, 0.35))
    ax3d.set_title("Fractal landscape")

    cbar = plt.colorbar(surf, ax=ax3d, fraction=0.03, pad=0.02)
    cbar.set_label("Elevation")

    plt.tight_layout()
    plt.show()


def plot_topographic_map(Z, contour_levels=45):
    n = Z.shape[0]
    x = np.linspace(0, 1, n)
    y = np.linspace(0, 1, n)
    X, Y = np.meshgrid(x, y)

    fig = plt.figure(figsize=(7, 7))
    ax2d = fig.add_subplot(1, 1, 1)

    levels = np.linspace(Z.min(), Z.max(), contour_levels)

    filled = ax2d.contourf(
        X, Y, Z,
        levels=levels,
        cmap="terrain"  
    )


    cbar = plt.colorbar(filled, ax=ax2d, fraction=0.046, pad=0.04)
    cbar.set_label("Elevation")

    ax2d.set_aspect("equal")
    ax2d.set_xticks([])
    ax2d.set_yticks([])
    ax2d.set_title("Topographical map")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    Z = diamond_square(n_power=9, roughness=0.62, seed=7)
    Z = smooth_cheap(Z, passes=2)

    plot_colored_3d(Z)
    plot_topographic_map(Z, contour_levels=45)
