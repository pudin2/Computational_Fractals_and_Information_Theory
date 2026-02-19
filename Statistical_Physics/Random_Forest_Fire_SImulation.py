import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.animation import PillowWriter


def forest_fire_steps(L: int, p: float, seed: int = 7):
    rng = np.random.default_rng(seed)

    forest = (rng.random((L, L)) < p)
    total_trees = int(forest.sum())
    state = np.zeros((L, L), dtype=np.uint8)
    state[forest] = 1

    if total_trees == 0:
        return [state], 0.0

    q = deque()
    for r in range(L):
        if forest[r, 0]:
            state[r, 0] = 2
            q.append((r, 0))

    frames = [state.copy()]

    while q:
        next_q = deque()
        while q:
            r, c = q.popleft()

            if r > 0 and state[r - 1, c] == 1:
                state[r - 1, c] = 2; next_q.append((r - 1, c))
            if r < L - 1 and state[r + 1, c] == 1:
                state[r + 1, c] = 2; next_q.append((r + 1, c))
            if c > 0 and state[r, c - 1] == 1:
                state[r, c - 1] = 2; next_q.append((r, c - 1))
            if c < L - 1 and state[r, c + 1] == 1:
                state[r, c + 1] = 2; next_q.append((r, c + 1))

            state[r, c] = 3  

        frames.append(state.copy())
        q = next_q

    burned_fraction = float((state == 3).sum()) / float(total_trees)
    return frames, burned_fraction


def save_fire_gif(L=150, p=0.60, seed=7, out="forest_fire.gif", fps=15, max_frames=500):
    frames, burned_fraction = forest_fire_steps(L, p, seed)

    if len(frames) > max_frames:
        step = max(1, len(frames) // max_frames)
        frames = frames[::step]

    cmap = ListedColormap(["white", "#37d837", "#ff2b2b", "#b35a00"])
    norm = BoundaryNorm([0, 1, 2, 3, 4], cmap.N)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axis("off")
    im = ax.imshow(frames[0], cmap=cmap, norm=norm, interpolation="nearest")
    ax.set_title(f"L={L}, p={p:.3f}, seed={seed} | burned={burned_fraction:.3f}")

    def update(i):
        im.set_data(frames[i])
        return (im,)

    ani = FuncAnimation(fig, update, frames=len(frames), interval=1000//fps, blit=True)
    ani.save(out, writer=PillowWriter(fps=fps))
    plt.close(fig)

    print(f"GIF saved in: {out}")
    print(f"Burned fraction = {burned_fraction:.6f}")


if __name__ == "__main__":
    save_fire_gif(L=150, p=0.60, seed=7, out="forest_fire.gif", fps=15)
