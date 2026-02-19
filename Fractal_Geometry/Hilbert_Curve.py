import turtle as t
import sys


def hilbert_curve(n: int, angle: int, step: float):
    
    if n == 0:
        return

    t.right(angle)
    hilbert_curve(n - 1, -angle, step)

    t.forward(step)
    t.left(angle)
    hilbert_curve(n - 1, angle, step)

    t.forward(step)
    hilbert_curve(n - 1, angle, step)

    t.left(angle)
    t.forward(step)
    hilbert_curve(n - 1, -angle, step)
    t.right(angle)


def run(n: int = 3, size: int = 200):
    
    if n < 0:
        raise ValueError("n must be >= 0")

    t.speed(0)
    t.tracer(False)

    t.penup()
    t.goto(-size / 2.0, size / 2.0)
    t.pendown()

    if n >= 1:
        step = size / (2 ** n - 1)
        hilbert_curve(n, 90, step)

    t.update()
    t.done()


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run(n)
