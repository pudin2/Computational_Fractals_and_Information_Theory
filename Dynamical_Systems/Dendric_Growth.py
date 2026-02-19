import numpy as np
import matplotlib.pyplot as plt


def dla_simulation(
    N=301,
    n_particles=2500,
    spawn_radius=110,
    kill_radius=140,
    stick_prob=1.0,
    seed=7,
    max_steps_per_particle=6000,
    use_8_neighbors=True
):
    rng = np.random.default_rng(seed)

    grid = np.zeros((N, N), dtype=np.uint8)
    c = N // 2
    grid[c, c] = 1

    if use_8_neighbors:
        steps = np.array([[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]], dtype=int)
    else:
        steps = np.array([[1,0],[-1,0],[0,1],[0,-1]], dtype=int)

    def random_point_on_circle(r):
        theta = rng.uniform(0, 2*np.pi)
        x = int(c + r*np.cos(theta))
        y = int(c + r*np.sin(theta))
        return x, y

    def inside(x, y):
        return 0 <= x < N and 0 <= y < N

    def touches_cluster(x, y):
        
        for dx, dy in steps:
            xx, yy = x + dx, y + dy
            if 0 <= xx < N and 0 <= yy < N and grid[yy, xx]:
                return True
        return False

    r_max = 1

    for _ in range(n_particles):
        spawn_r = max(spawn_radius, r_max + 10)
        kill_r = max(kill_radius, spawn_r + 20)

        x, y = random_point_on_circle(spawn_r)

        for _step in range(max_steps_per_particle):
            if not inside(x, y):
                x, y = random_point_on_circle(spawn_r)
                continue

            dx = x - c
            dy = y - c
            if dx*dx + dy*dy > kill_r*kill_r:
                x, y = random_point_on_circle(spawn_r)
                continue

            if touches_cluster(x, y) and rng.random() <= stick_prob:
                grid[y, x] = 1
                r = int(np.sqrt(dx*dx + dy*dy))
                if r > r_max:
                    r_max = r
                break

            sx, sy = steps[rng.integers(0, len(steps))]
            x += sx
            y += sy

    return grid


def run_single_seed(seed=7):
    grid = dla_simulation(
        N=251,
        n_particles=12000,
        spawn_radius=90,
        kill_radius=120,
        stick_prob=1.0,
        seed=seed,
        max_steps_per_particle=12000,
        use_8_neighbors=True
    )

    plt.figure(figsize=(6, 6))
    plt.imshow(grid, cmap="gray", interpolation="nearest")
    plt.title(f"DLA dendritic growth (seed={seed})")
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    run_single_seed(seed=7)
