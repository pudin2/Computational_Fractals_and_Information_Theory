import turtle as t
import sys


AXIOM = "FXF--FF--FF"
RULES = {
    "F": "FF",
    "X": "--FXF++FXF++FXF--"
}

def expand_lsystem(axiom: str, rules: dict[str, str], iterations: int) -> str:
    s = axiom
    for _ in range(iterations):
        s = "".join(rules.get(ch, ch) for ch in s)
    return s


def draw_lsystem(commands: str, step: float, angle: float):
    for ch in commands:
        if ch == "F":
            t.forward(step)
        elif ch == "+":
            t.left(angle)
        elif ch == "-":
            t.right(angle)


def run(iterations=6, step=4.0, angle=60.0, start_pos=(-250, 150)):
    t.title("Sierpinski Triangle (L-system)")
    t.speed(0)
    t.tracer(False)
    t.hideturtle()

    t.penup()
    t.goto(*start_pos)
    t.pendown()

    commands = expand_lsystem(AXIOM, RULES, iterations)
    draw_lsystem(commands, step, angle)

    t.update()
    t.done()


if __name__ == "__main__":

    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    step = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
    run(iterations=iterations, step=step)
