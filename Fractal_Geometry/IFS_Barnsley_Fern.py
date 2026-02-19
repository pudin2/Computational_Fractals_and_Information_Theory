import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def f1(x, y):
    return 0.0, 0.16 * y

def f2(x, y):
    return (0.85 * x + 0.04 * y,
            -0.04 * x + 0.85 * y + 1.6)

def f3(x, y):
    return (0.20 * x - 0.26 * y,
            0.23 * x + 0.22 * y + 1.6)

def f4(x, y):
    return (-0.15 * x + 0.28 * y,
            0.26 * x + 0.24 * y + 0.44)

funciones = [f1, f2, f3, f4]

width, height = 300, 300
imagen = np.zeros((height, width), dtype=np.uint8)

puntos = 100000
x, y = 0.0, 0.0

for _ in range(puntos):
    funcion = np.random.choice(funciones, p=[0.01, 0.85, 0.07, 0.07])
    x, y = funcion(x, y)

    ix = int(width / 2 + x * width / 10)
    iy = int(y * height / 12)

    if 0 <= ix < width and 0 <= iy < height:
        imagen[iy, ix] = 255

plt.imshow(imagen[::-1, :], cmap=cm.Greys, interpolation="nearest")
plt.axis("off")
plt.show()
