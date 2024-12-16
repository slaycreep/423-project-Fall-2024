from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# end of imports


canyon_top = [{"x": i, "y": random.randint(60, 100)} for i in range(0, 600, 20)]

c = 0
b = 0
sky = (0.53, 0.81, 0.92, 1)


def draw_points(x, y, r, g, b):
    glPointSize(2)
    glBegin(GL_POINTS)
    glColor3f(r, g, b)
    glVertex2f(x, y)
    glEnd()


def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) > abs(dy):
        if dx >= 0 and dy >= 0:
            return 0
        elif dx <= 0 and dy >= 0:
            return 3
        elif dx <= 0 and dy <= 0:
            return 4
        elif dx >= 0 and dy <= 0:
            return 7
    else:
        if dx >= 0 and dy >= 0:
            return 1
        elif dx <= 0 and dy >= 0:
            return 2
        elif dx <= 0 and dy <= 0:
            return 5
        elif dx >= 0 and dy <= 0:
            return 6


def convert_M_to_0(x, y, zone):
    if zone == 0:
        return (x, y)
    elif zone == 1:
        return (y, x)
    elif zone == 2:
        return (y, -x)
    elif zone == 3:
        return (-x, y)
    elif zone == 4:
        return (-x, -y)
    elif zone == 5:
        return (-y, -x)
    elif zone == 6:
        return (-y, x)
    elif zone == 7:
        return (x, -y)


def convert_0_to_M(x, y, zone):
    if zone == 0:
        return (x, y)
    elif zone == 1:
        return (y, x)
    elif zone == 2:
        return (-y, x)
    elif zone == 3:
        return (-x, y)
    elif zone == 4:
        return (-x, -y)
    elif zone == 5:
        return (-y, -x)
    elif zone == 6:
        return (y, -x)
    elif zone == 7:
        return (x, -y)


def MidpointLine(nx1, ny1, nx2, ny2, zone, r, g, b):
    ndx = nx2 - nx1
    ndy = ny2 - ny1
    d = 2 * ndy - ndx
    incE = 2 * ndy
    incNE = 2 * (ndy - ndx)
    y = ny1
    x = nx1
    cx, cy = convert_0_to_M(x, y, zone)
    draw_points(cx, cy, r, g, b)
    while x < nx2:
        if d <= 0:
            d += incE
            x += 1
        else:
            d += incNE
            x += 1
            y += 1
        cx, cy = convert_0_to_M(x, y, zone)
        draw_points(cx, cy, r, g, b)


def eightway(x1, y1, x2, y2, r, g, b):
    zone = find_zone(x1, y1, x2, y2)
    nx1, ny1 = convert_M_to_0(x1, y1, zone)
    nx2, ny2 = convert_M_to_0(x2, y2, zone)
    MidpointLine(nx1, ny1, nx2, ny2, zone, r, g, b)


def d_update(d, x, y, direction):
    if direction == "SE":
        return d + (2 * x) - (2 * y) + 5
    else:
        return d + (2 * x) + 3


def circlepoints(x, y, cx, cy, r, g, b):
    draw_points(x + cx, y + cy, r, g, b)
    draw_points(y + cx, x + cy, r, g, b)
    draw_points(y + cx, -x + cy, r, g, b)
    draw_points(x + cx, -y + cy, r, g, b)
    draw_points(-x + cx, -y + cy, r, g, b)
    draw_points(-y + cx, -x + cy, r, g, b)
    draw_points(-y + cx, x + cy, r, g, b)
    draw_points(-x + cx, y + cy, r, g, b)


def circle(radius, r, g, b, cx=0, cy=0):
    d = 1 - radius
    x = 0
    y = radius
    circlepoints(x, y, cx, cy, r, g, b)
    while x <= y:
        if d >= 0:
            d += 2 * (x - y) + 5
            x += 1
            y -= 1
        else:
            d += (2 * x) + 3
            x += 1
        circlepoints(x, y, cx, cy, r, g, b)


def fill_circle_with_points(cx, cy, radius, r, g, b):
    glColor3f(r, g, b)  # Set the fill color
    glBegin(GL_POINTS)
    for x in range(cx - radius, cx + radius + 1):
        for y in range(cy - radius, cy + radius + 1):
            if (x - cx) ** 2 + (
                y - cy
            ) ** 2 <= radius**2:  # Check if the point is inside the circle
                glVertex2f(x, y)
    glEnd()


# canyon code
def update_canyon_top():
    global canyon_top
    for point in canyon_top:
        point["x"] -= 2  # Move left
    if canyon_top[0]["x"] < 0:
        canyon_top.pop(0)  # Remove leftmost point
        new_x = canyon_top[-1]["x"] + 20  # Add new point to the right
        new_y = canyon_top[-1]["y"] + random.randint(-10, 10)  # Random y offset
        new_y = max(50, min(150, new_y))  # Clamp y value
        canyon_top.append({"x": new_x, "y": new_y})


def draw_canyon_top():
    for i in range(len(canyon_top) - 1):
        x0, y0 = canyon_top[i]["x"], canyon_top[i]["y"]
        x1, y1 = canyon_top[i + 1]["x"], canyon_top[i + 1]["y"]
        eightway(int(x0), int(y0), int(x1), int(y1), 0.58, 0.29, 0)


def balloons(b):
    circle(25, 0, 0, 0.5, 100, 275 + b)  # circle of balloon
    fill_circle_with_points(100, 275 + b, 25, 0, 0, 0.5)  # Filled red circle
    eightway(80, 235 + b, 120, 235 + b, 0.58, 0.29, 0)  # box
    eightway(80, 235 + b, 85, 215 + b, 0.58, 0.29, 0)
    eightway(120, 235 + b, 115, 215 + b, 0.58, 0.29, 0)
    eightway(85, 215 + b, 115, 215 + b, 0.58, 0.29, 0)

    eightway(80, 235 + b, 80, 260 + b, 0.58, 0.29, 0)  # ropes
    eightway(120, 235 + b, 120, 260 + b, 0.58, 0.29, 0)
    eightway(100, 250 + b, 100, 235 + b, 0.58, 0.29, 0)
    
class balloon_hitbox():
    def __init__(self, b):
        self.xmin = 85
        self.ymin = 215 +  b
        self.xmax = 125
        self.ymax = 300 + b
        self.height = self.ymax - self.ymin
        self.width = self.xmax - self.xmin

def specialKeyListener(key, x, y):
    global b
    if key == GLUT_KEY_UP:
        b += 10
    if key == GLUT_KEY_DOWN:  # // up arrow key
        b -= 10
    glutPostRedisplay()


def animation():
    update_canyon_top()
    glutPostRedisplay()
    # glutTimerFunc(16, animation, 0)


def iterate():
    glViewport(0, 0, 600, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 600, 0.0, 500, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def showScreen():
    global c, b
    glClearColor(*sky)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glColor3f(1.0, 1.0, 0.0)  # konokichur color set (RGB)
    # call the draw methods here
    balloons(b)
    draw_canyon_top()
    glutSwapBuffers()


glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(600, 500)  # window size
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"Up And Away!")  # window name
glutDisplayFunc(showScreen)
glutIdleFunc(animation)
glutSpecialFunc(specialKeyListener)
glutMainLoop()
