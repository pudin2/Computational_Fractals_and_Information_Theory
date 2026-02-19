import math
import pathlib
import tkinter as tk
from tkinter import filedialog
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def select_image_file() -> pathlib.Path:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="Select an image (PNG/JPG/BMP)",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
    )
    root.destroy()
    if not path:
        raise SystemExit("No file selected.")
    return pathlib.Path(path)


def to_grayscale_float(img: Image.Image, size=(256, 256)) -> np.ndarray:

    g = img.convert("L").resize(size, Image.BILINEAR)
    arr = np.asarray(g, dtype=np.float32) / 255.0
    return arr


def downsample2x(block: np.ndarray) -> np.ndarray:

    h, w = block.shape
    assert h % 2 == 0 and w % 2 == 0
    return 0.25 * (block[0:h:2, 0:w:2] + block[1:h:2, 0:w:2] + block[0:h:2, 1:w:2] + block[1:h:2, 1:w:2])


def apply_isometry(block: np.ndarray, t_id: int) -> np.ndarray:

    if t_id == 0:
        return block
    if t_id == 1:
        return np.rot90(block, 1)
    if t_id == 2:
        return np.rot90(block, 2)
    if t_id == 3:
        return np.rot90(block, 3)
    if t_id == 4:
        return np.fliplr(block)
    if t_id == 5:
        return np.flipud(block)
    if t_id == 6:
        return block.T
    if t_id == 7:
        return np.fliplr(block.T)
    raise ValueError("t_id must be 0..7")


def fit_affine(D: np.ndarray, R: np.ndarray, s_clip=(-1.0, 1.0)) -> tuple[float, float, float]:

    d = D.reshape(-1)
    r = R.reshape(-1)

    d_mean = float(d.mean())
    r_mean = float(r.mean())
    var_d = float(((d - d_mean) ** 2).mean())

    if var_d < 1e-12:
        s = 0.0
    else:
        cov = float(((d - d_mean) * (r - r_mean)).mean())
        s = cov / var_d

    s = float(np.clip(s, s_clip[0], s_clip[1]))
    o = r_mean - s * d_mean

    pred = s * D + o
    mse = float(((pred - R) ** 2).mean())
    return s, o, mse

def psnr(img1: np.ndarray, img2: np.ndarray) -> float:
    mse = float(((img1 - img2) ** 2).mean())
    if mse < 1e-12:
        return 99.0
    return 10.0 * math.log10(1.0 / mse)

def fractal_encode(
    img: np.ndarray,
    rsize: int = 8,
    domain_stride: int = 4,
    window_size: int | None = None,
    max_domains_per_range: int | None = None
) -> dict:

    H, W = img.shape
    assert H % rsize == 0 and W % rsize == 0
    dsize = 2 * rsize

    domain_positions = []
    for y in range(0, H - dsize + 1, domain_stride):
        for x in range(0, W - dsize + 1, domain_stride):
            domain_positions.append((y, x))
    domain_positions = np.array(domain_positions, dtype=np.int32)

    nRy = H // rsize
    nRx = W // rsize

    codes = []
    for ry in range(nRy):
        for rx in range(nRx):
            yR = ry * rsize
            xR = rx * rsize
            R = img[yR:yR + rsize, xR:xR + rsize]

            candidates = domain_positions

            if window_size is not None:

                cy = yR + rsize // 2
                cx = xR + rsize // 2

                dy = candidates[:, 0] + dsize // 2
                dx = candidates[:, 1] + dsize // 2
                mask = (np.abs(dy - cy) <= window_size) & (np.abs(dx - cx) <= window_size)
                candidates = candidates[mask]
                if len(candidates) == 0:
                    candidates = domain_positions  

            if max_domains_per_range is not None and len(candidates) > max_domains_per_range:
                idx = np.random.choice(len(candidates), size=max_domains_per_range, replace=False)
                candidates = candidates[idx]

            best = (1e9, None)  
            for (yD, xD) in candidates:
                D_big = img[yD:yD + dsize, xD:xD + dsize]
                D = downsample2x(D_big)  

                for t_id in range(8):
                    Dt = apply_isometry(D, t_id)
                    s, o, mse = fit_affine(Dt, R, s_clip=(-1.0, 1.0))
                    if mse < best[0]:
                        best = (mse, (yD, xD, t_id, s, o))

            yD, xD, t_id, s, o = best[1]
            codes.append((yD, xD, t_id, float(s), float(o)))

    return {
        "H": H, "W": W,
        "rsize": rsize,
        "domain_stride": domain_stride,
        "codes": np.array(codes, dtype=np.float32)  
    }

def fractal_decode(model: dict, n_iters: int = 10, init: str = "gray") -> np.ndarray:
    H, W = int(model["H"]), int(model["W"])
    rsize = int(model["rsize"])
    dsize = 2 * rsize
    codes = model["codes"]  

    nRy = H // rsize
    nRx = W // rsize

    if init == "random":
        cur = np.random.rand(H, W).astype(np.float32)
    else:
        cur = np.full((H, W), 0.5, dtype=np.float32)

    for _ in range(n_iters):
        nxt = np.empty_like(cur)
        idx = 0
        for ry in range(nRy):
            for rx in range(nRx):
                yR = ry * rsize
                xR = rx * rsize

                yD = int(codes[idx, 0])
                xD = int(codes[idx, 1])
                t_id = int(codes[idx, 2])
                s = float(codes[idx, 3])
                o = float(codes[idx, 4])

                D_big = cur[yD:yD + dsize, xD:xD + dsize]
                D = downsample2x(D_big)
                Dt = apply_isometry(D, t_id)
                R_hat = s * Dt + o
                nxt[yR:yR + rsize, xR:xR + rsize] = np.clip(R_hat, 0.0, 1.0)

                idx += 1

        cur = nxt

    return cur

def main():
    path = select_image_file()
    img = Image.open(path)

    original = to_grayscale_float(img, size=(256, 256))

    model = fractal_encode(
        original,
        rsize=8,
        domain_stride=4,
        window_size=64,              
        max_domains_per_range=800    
    )

    recon = fractal_decode(model, n_iters=10, init="gray")

    p = psnr(original, recon)
    print(f"PSNR: {p:.2f} dB")

    approx_bytes = model["codes"].size * 4  
    orig_bytes = original.size  
    print(f"Approx model bytes: {approx_bytes:,}")
    print(f"Pixels: {original.shape[0]}x{original.shape[1]} ({orig_bytes:,} pixels)")

    plt.figure()
    plt.imshow(original, cmap="gray")
    plt.title("Original")
    plt.axis("off")

    plt.figure()
    plt.imshow(recon, cmap="gray")
    plt.title(f"Reconstructed (PSNR {p:.2f} dB)")
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    main()
