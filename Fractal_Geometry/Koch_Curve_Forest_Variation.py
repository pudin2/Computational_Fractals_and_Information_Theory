import turtle
import sys


def koch_curve(t, order, size):

    if order == 0:
        t.forward(size)
        return

    for angle in [85, -170, 85, 0]:
        koch_curve(t, order - 1, size / 2)
        t.right(angle)


def run(order=5, size=300, bg="black", color="white"):
    turtle.title("Koch")
    screen = turtle.Screen()
    screen.bgcolor(bg)

    st = turtle.Turtle(visible=False)
    st.speed(0)           
    turtle.tracer(False)   

    st.color(color)
    st.penup()
    st.goto(size / (-2) - 80, size / 2 + 80)
    st.pendown()

    for _ in range(4):
        koch_curve(st, order, size)
        st.right(90)

    turtle.update()
    turtle.done()


if __name__ == "__main__":
    order = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    size = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    run(order, size)
