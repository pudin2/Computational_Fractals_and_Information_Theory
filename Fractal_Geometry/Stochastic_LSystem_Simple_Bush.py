import random
import turtle as t

def expand_stochastic(axiom: str, rules: dict[str, list[tuple[str, float]]], iterations: int, seed: int | None = None) -> str:
    if seed is not None:
        random.seed(seed)

    s = axiom
    for _ in range(iterations):
        out = []
        for ch in s:
            if ch in rules:
                choices = rules[ch]
                repl = random.choices(
                    population=[r for r, _ in choices],
                    weights=[p for _, p in choices],
                    k=1
                )[0]
                out.append(repl)
            else:
                out.append(ch)
        s = "".join(out)
    return s

def draw_lsystem(
    commands: str,
    step: float = 6.0,
    angle: float = 22.5,
    step_jitter: float = 0.15,
    angle_jitter: float = 0.12,
    seed: int | None = None
):
    if seed is not None:
        random.seed(seed + 999)

    stack = []

    for ch in commands:
        if ch == "F":
            s = step * (1.0 + random.uniform(-step_jitter, step_jitter))
            t.forward(s)
        elif ch == "+":
            a = angle * (1.0 + random.uniform(-angle_jitter, angle_jitter))
            t.left(a)
        elif ch == "-":
            a = angle * (1.0 + random.uniform(-angle_jitter, angle_jitter))
            t.right(a)
        elif ch == "[":
            stack.append((t.position(), t.heading()))
        elif ch == "]":
            pos, heading = stack.pop()
            t.penup()
            t.goto(pos)
            t.setheading(heading)
            t.pendown()

def draw_bush(seed: int, start_pos: tuple[float, float], iterations: int, step: float, angle: float):
    axiom = "F"
    rules = {
        "F": [
            ("F[+F]F[-F]F", 0.45),
            ("F[+F]F",      0.20),
            ("F[-F]F",      0.20),
            ("F[+F][-F]F",  0.15),
        ]
    }

    commands = expand_stochastic(axiom, rules, iterations, seed=seed)

    t.penup()
    t.goto(*start_pos)
    t.setheading(90)
    t.pendown()

    t.penup()
    t.goto(start_pos[0], start_pos[1] - 30)
    t.pendown()
    t.write(f"seed={seed}", align="center", font=("Arial", 12, "normal"))

    t.penup()
    t.goto(*start_pos)
    t.setheading(90)
    t.pendown()

    draw_lsystem(
        commands,
        step=step,
        angle=angle,
        step_jitter=0.20,
        angle_jitter=0.10,
        seed=seed
    )

def run_three_seeds(seeds=(1, 7, 42), iterations=5, step=7.0, angle=22.5):
    t.title("Stochastic L-System - Simple Bush (3 seeds)")
    t.bgcolor("white")
    t.colormode(255)
    t.hideturtle()
    t.speed(0)
    t.tracer(False)
    t.pencolor(20, 120, 20)
    t.pensize(2)

    y0 = -260
    x_positions = [-250, 0, 250]

    for x0, seed in zip(x_positions, seeds):
        draw_bush(seed, (x0, y0), iterations, step, angle)

    t.update()
    t.done()

if __name__ == "__main__":
    run_three_seeds(seeds=(1, 7, 42), iterations=7, step=7.0, angle=22.5)
