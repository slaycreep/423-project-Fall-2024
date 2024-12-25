from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# end of imports


canyon_top = [{"x": i, "y": random.randint(60, 100)} for i in range(0, 600, 20)]

c = 0
b = 0
cl = 0
sky = (0.53, 0.81, 0.92, 1)
clouds = []
birds = []
gameover = False
fuel_level = 100

# powerups array
fuel_cans = []


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


class balloon_hitbox:
    def __init__(self, b):
        self.xmin = 75
        self.ymin = 215 + b
        self.xmax = 125
        self.ymax = 300 + b
        self.height = self.ymax - self.ymin
        self.width = self.xmax - self.xmin


def cloud():
    y = random.randint(200, 450)
    if len(clouds) == 0 and random.randint(1, 100) == 10:
        clouds.append([25, 0.69, 0.74, 0.71, 530, y])
        clouds.append([25, 0.69, 0.74, 0.71, 550, y])
        clouds.append([25, 0.69, 0.74, 0.71, 580, y])
        clouds.append([25, 0.69, 0.74, 0.71, 550, y + 20])


class cloud_hitbox:
    def __init__(self, arr, cl):
        self.xmin = arr[0][4] - arr[0][0] + cl
        self.ymin = arr[0][5] - arr[0][0]
        self.xmax = arr[2][4] + arr[2][0] + cl
        self.ymax = arr[3][5] + arr[3][0]
        self.height = self.ymax - self.ymin
        self.width = self.xmax - self.xmin


def draw_clouds():
    global clouds, cl
    if len(clouds) != 0:
        for i in range(0, len(clouds) - 1, 4):
            if clouds[0][4] - clouds[0][0] + cl <= 0:
                clouds = []
            else:
                circle(
                    clouds[i][0],
                    clouds[i][1],
                    clouds[i][2],
                    clouds[i][3],
                    clouds[i][4] + cl,
                    clouds[i][5],
                )
                circle(
                    clouds[i + 1][0],
                    clouds[i + 1][1],
                    clouds[i + 1][2],
                    clouds[i + 1][3],
                    clouds[i + 1][4] + cl,
                    clouds[i + 1][5],
                )
                circle(
                    clouds[i + 2][0],
                    clouds[i + 2][1],
                    clouds[i + 2][2],
                    clouds[i + 2][3],
                    clouds[i + 2][4] + cl,
                    clouds[i + 2][5],
                )
                circle(
                    clouds[i + 3][0],
                    clouds[i + 3][1],
                    clouds[i + 3][2],
                    clouds[i + 3][3],
                    clouds[i + 3][4] + cl,
                    clouds[i + 3][5],
                )

                fill_circle_with_points(
                    clouds[i][4] + cl,
                    clouds[i][5],
                    clouds[i][0],
                    clouds[i][1],
                    clouds[i][2],
                    clouds[i][3],
                )
                fill_circle_with_points(
                    clouds[i + 1][4] + cl,
                    clouds[i + 1][5],
                    clouds[i + 1][0],
                    clouds[i + 1][1],
                    clouds[i + 1][2],
                    clouds[i + 1][3],
                )
                fill_circle_with_points(
                    clouds[i + 2][4] + cl,
                    clouds[i + 2][5],
                    clouds[i + 2][0],
                    clouds[i + 2][1],
                    clouds[i + 2][2],
                    clouds[i + 2][3],
                )
                fill_circle_with_points(
                    clouds[i + 3][4] + cl,
                    clouds[i + 3][5],
                    clouds[i + 3][0],
                    clouds[i + 3][1],
                    clouds[i + 3][2],
                    clouds[i + 3][3],
                )


def move_clouds():
    global cl, clouds
    if len(clouds) == 0:
        cl = 0
    else:
        cl -= 5


def fuel_bar():
    current_height = 400 + (fuel_level * 0.8)

    for y in range(400, int(current_height)):
        eightway(11, y, 49, y, 1, 1, 0)

    eightway(10, 480, 50, 480, 0.58, 0.29, 0)  # Top border
    eightway(10, 400, 50, 400, 0.58, 0.29, 0)  # Bottom border
    eightway(10, 400, 10, 480, 0.58, 0.29, 0)  # Left border
    eightway(50, 400, 50, 480, 0.58, 0.29, 0)  # Right border


# powerups related code
def fuel_powerup():
    y = random.randint(300, 500)
    if len(fuel_cans) == 0 and random.randint(1, 50) == 10:
        # Add a single fuel can with position and movement info
        fuel_cans.append({"x": 530, "y": y, "radius": 25, "move": 0})


def draw_fuel_cans():
    global fuel_cans
    for can in fuel_cans:
        if can["x"] + can["move"] <= 0:
            fuel_cans.remove(can)
        else:
            # Draw outer circle
            circle(can["radius"], 1, 0.84, 0, can["x"] + can["move"], can["y"])
            # Fill circle
            fill_circle_with_points(
                can["x"] + can["move"], can["y"], can["radius"], 1, 0.84, 0
            )
            # Draw fuel can symbol
            # bottom
            eightway(
                can["x"] - 10 + can["move"],
                can["y"] - 5,
                can["x"] + 10 + can["move"],
                can["y"] - 5,
                0,
                0,
                0,
            )
            # top
            eightway(
                can["x"] - 10 + can["move"],
                can["y"] + 10,
                can["x"] + 10 + can["move"],
                can["y"] + 10,
                0,
                0,
                0,
            )
            # left
            eightway(
                can["x"] - 10 + can["move"],
                can["y"] - 5,
                can["x"] - 10 + can["move"],
                can["y"] + 10,
                0,
                0,
                0,
            )
            # right
            eightway(
                can["x"] + 10 + can["move"],
                can["y"] - 5,
                can["x"] + 10 + can["move"],
                can["y"] + 10,
                0,
                0,
                0,
            )
            can["move"] -= 2


# draw a bird
def bird_figure(x, y):
    random_color = (random.random(), random.random(), random.random())
    eightway(x, y, x + 15, y - 10, 0, 0, 0)
    eightway(x, y, x + 15, y + 10, 0, 0, 0)
    # tail
    eightway(x + 15, y - 10, x + 15, y - 5, 0, 0, 0)
    eightway(x + 15, y + 10, x + 15, y + 5, 0, 0, 0)
    eightway(x + 15, y - 5, x + 20, y, 0, 0, 0)
    eightway(x + 15, y + 5, x + 20, y, 0, 0, 0)


def generate_birds():
    global birds
    if len(birds) == 0 and random.randint(1, 100) == 10:
        x = 600
        y = random.randint(200, 400)
        birds.append([x, y])
        birds.append([x + 10, y + 20])
        birds.append([x + 15, y - 20])


def draw_birds():
    global birds
    print(birds)
    for bird in birds:
        if bird[0] <= 0:
            birds.remove(bird)
        else:
            bird[0] -= 2
            bird_figure(bird[0], bird[1])


def specialKeyListener(key, x, y):
    global b, fuel_level, gameover
    if fuel_level <= 0:
        gameover = True
        return

    if key == GLUT_KEY_UP:
        b += 8
        fuel_level = max(0, fuel_level - 0.5)
    if key == GLUT_KEY_DOWN:
        b -= 8
        fuel_level = max(0, fuel_level - 0.5)
    glutPostRedisplay()


def animation():
    global gameover, b
    if not gameover:
        update_canyon_top()
        move_clouds()
        # draw_fuel_cans()
        b -= 1  # gravity
    glutPostRedisplay()
    # glutTimerFunc(16, animation, 0)


def iterate():
    glViewport(0, 0, 600, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 600, 0.0, 500, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def check_collision():
    balloon = balloon_hitbox(b)

    for i in range(len(canyon_top) - 1):
        current_point = canyon_top[i]
        next_point = canyon_top[i + 1]

        # Check if balloon is within the x-range of these canyon points
        if balloon.xmin <= next_point["x"] and balloon.xmax >= current_point["x"]:
            if balloon.ymin <= current_point["y"]:
                print("Collided with canyon!")
                return True

    return False


def cloud_collision():
    global clouds, cl
    bb = balloon_hitbox(b)
    cc = cloud_hitbox(clouds, cl)
    return (
        (bb.xmin) < (cc.xmin + cc.width)
        and (bb.xmin + bb.width) > (cc.xmin)
        and (bb.ymin) < (cc.ymin + cc.height)
        and (bb.ymin + bb.height) > (cc.ymin)
    )


class FuelCanHitbox:
    def __init__(self, can):
        self.xmin = can["x"] - can["radius"] + can["move"]
        self.ymin = can["y"] - can["radius"]
        self.xmax = can["x"] + can["radius"] + can["move"]
        self.ymax = can["y"] + can["radius"]
        self.height = self.ymax - self.ymin
        self.width = self.xmax - self.xmin


def fuel_can_collision():
    global fuel_cans
    bb = balloon_hitbox(b)
    for can in fuel_cans:
        fc = FuelCanHitbox(can)
        return (
            (bb.xmin) < (fc.xmin + fc.width)
            and (bb.xmin + bb.width) > (fc.xmin)
            and (bb.ymin) < (fc.ymin + fc.height)
            and (bb.ymin + bb.height) > (fc.ymin)
        )


class BirdHitbox:
    def __init__(self, bird):
        self.xmin = bird[0]
        self.ymin = bird[1]
        self.xmax = bird[0] + 20
        self.ymax = bird[1] + 20
        self.height = self.ymax - self.ymin
        self.width = self.xmax - self.xmin


def check_bird_collision():
    global birds
    bb = balloon_hitbox(b)
    for bird in birds:
        fc = BirdHitbox(bird)
        return (
            (bb.xmin) < (fc.xmin + fc.width)
            and (bb.xmin + bb.width) > (fc.xmin)
            and (bb.ymin) < (fc.ymin + fc.height)
            and (bb.ymin + bb.height) > (fc.ymin)
        )


def showScreen():
    global c, b, gameover, fuel_level
    glClearColor(*sky)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glColor3f(1.0, 1.0, 0.0)  # konokichur color set (RGB)
    # call the draw methods here
    if not gameover:
        balloons(b)
        draw_canyon_top()
        cloud()
        draw_clouds()
        fuel_bar()
        # bird code
        generate_birds()
        draw_birds()
        fuel_powerup()
        draw_fuel_cans()
        if check_collision() == True:
            gameover = True
        if len(clouds) != 0:
            if cloud_collision() == True:
                print("Collided with cloud!")
                gameover = True
        if fuel_can_collision() == True:
            print("Collided with fuel can!")
            fuel_level = min(100, fuel_level + 10)
            fuel_cans.pop()
        if check_bird_collision() == True:
            print("Collided with bird!")
            gameover = True

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
