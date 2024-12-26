from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# end of imports


# ---global variables---
canyon_top = [{"x": i, "y": random.randint(60, 100)} for i in range(0, 600, 20)]
c = 0
b = 0
cl = 0
sky = (0.53, 0.81, 0.92, 1)
clouds = []
gameover = False
slowmo = False
slow = []
slowmo_start_time = None
start_time = time.time()
pause_time = 0
pause_start_time = None
print_score = True

fuel_level = 100
fuel_cans = []
birds = []

game_state="Playing"

# control speed
global_obejct_speed = 6
s = 0


# ---end of global variables---


# ---core algorithms---
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


# ---end of core algorithms---


# ----Canyon related code----
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


def check_collision_with_canyon():

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


# ----end of Canyon related code----


# ----Balloon related code----
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


# ----end of Balloon related code----


# ----Cloud related code----
def cloud():
    y = random.randint(250, 480)  # cloud's vertical position will be generated randomly
    if len(clouds) == 0 and random.randint(1, 200) == 10:
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
            if (
                clouds[0][4] - clouds[0][0] + cl <= 0
            ):  # checking whether cloud has travelled to leftmost corner of screeen
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
    global cl, clouds, s, global_obejct_speed
    if len(clouds) == 0:
        cl = 0
    else:
        cl = cl - (
            global_obejct_speed - s
        )  # s is the variable which is actiavted when slowmode is on, so clouds will move slowly


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
# ----end of Cloud related code----


# ----Fuel related code----
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
    global fuel_cans,global_obejct_speed
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
            if game_state == "Playing":
                can["move"] -= (global_obejct_speed - s)


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


# ----end of Fuel related code----


# ----Bird related code----
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
    global birds, global_obejct_speed, game_state
    print(birds)
    for bird in birds:
        if bird[0] <= 0:
            birds.remove(bird)
        else:
            if game_state == "Playing": 
                bird[0] -= (global_obejct_speed - s)

            bird_figure(bird[0], bird[1])


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


# ----end of Bird related code----


# ----aeroplane related code----
def planes_initVal():
    global planeLst, planeSpeed, lstCreatedPlane
    planeLst = []
    planeSpeed = 2
    lstCreatedPlane = time.time()


def drawAeroplane():
    global planeLst  # planeX,0  #, catcher_width, catcher_color
    if len(planeLst) != 0:

        for plane in planeLst:
            planeX = plane["planeX"]
            planeY = plane["planeY"]
            eightway(planeX, planeY + 20, planeX + 60, planeY + 20, 1, 1, 1)
            eightway(planeX + 20, planeY + 30, planeX + 50, planeY + 30, 1, 1, 1)
            eightway(planeX, planeY + 20, planeX + 20, planeY + 30, 1, 1, 1)
            eightway(planeX + 60, planeY + 20, planeX + 60, planeY + 40, 1, 1, 1)
            eightway(planeX + 50, planeY + 30, planeX + 60, planeY + 40, 1, 1, 1)


def create_plane():
    global planeLst

    planeInfo = {"planeY": random.randint(200, 400), "planeX": 600}
    planeLst.append(planeInfo)


def update_planes():
    global planeLst, planeSpeed, s, global_obejct_speed
    for plane in planeLst:
        if plane["planeX"] < -230:
            planeLst.remove(plane)
        else:
            plane["planeX"] -= (global_obejct_speed - s)


def check_planes():
    global lstCreatedPlane
    curTime = time.time()
    if curTime - lstCreatedPlane >= 15:
        create_plane()
        lstCreatedPlane = time.time()

def check_airplane_balloon_collision():
    global planeLst, gameover
    balloon = balloon_hitbox(b)  # Balloon hitbox

    for plane in planeLst:
        # Define plane hitbox
        plane_hitbox = {
            'xmin': plane['planeX'],
            'ymin': plane['planeY'] + 20,
            'xmax': plane['planeX'] + 60,
            'ymax': plane['planeY'] + 40,
        }

        # AABB Collision Check
        if (
            balloon.xmin < plane_hitbox['xmax']
            and balloon.xmax > plane_hitbox['xmin']
            and balloon.ymin < plane_hitbox['ymax']
            and balloon.ymax > plane_hitbox['ymin']
        ):
            return True  # Collision detected

    return False  # No collision
# ----end of aeroplane related code----

# ----Slow motion related code----
def slow_motion():
    global slow
    if not gameover:
        a = random.randint(90, 400)
        slow.append([14, 600, random.randint(90, 400), 1, 1, 0])


def move_slow(arr):  # falling motion of slow
    if not gameover:
        for i in range(len(arr)):
            if arr[i][1] > 0:
                arr[i][1] -= 5


def collide_slowmo(arr):
    if len(arr) != 0:
        balloon = balloon_hitbox(b)
        cxmin = arr[0][1] - arr[0][0]
        cymin = arr[0][2] - arr[0][0]
        cwidth, cheight = (2 * arr[0][0], 2 * arr[0][0])
        return (
            (balloon.xmin) < (cxmin + cwidth)
            and (balloon.xmin + balloon.width) > (cxmin)
            and (balloon.ymin) < (cymin + cheight)
            and (balloon.ymin + balloon.height) > (cymin)
        )


def activate_slow_mo():
    global slowmo, slowmo_start_time, s
    slowmo = True
    slowmo_start_time = time.time()
    s = 3
    print("Slow motion activated!")



def update_slow_mo():
    global slowmo, slowmo_start_time, s
    if slowmo and (
        time.time() - slowmo_start_time >= 5
    ):  # slow mode will be activated for 5 sec
        slowmo = False
        s = 0
        print("Slow motion deactivated!")
# ----end of Slow motion related code----




#----button related code----
def close():
    glColor3f(0,0,0)
    eightway(350, 470, 370, 490,1,1,1)  # Shifted right by 100
    eightway(350, 490, 370, 470,1,1,1)  # Shifted right by 100

def pause():
    glColor3f(0,0,0)
    eightway(300, 470, 300, 490,1,1,1)  # Shifted right by 55
    eightway(310, 470, 310, 490,1,1,1)  # Shifted right by 55

def resume():
    glColor3f(0,0,0)
    eightway(300, 470, 300, 490,1,1,1)  # Shifted right by 55
    eightway(300, 470, 320, 480,1,1,1)  # Shifted right by 55
    eightway(300, 490, 320, 480,1,1,1)  # Shifted right by 55

def back():
    glColor3f(0,0,0)
    eightway(240, 480, 270, 480,1,1,1)
    eightway(240, 480, 255, 490,1,1,1)
    eightway(240, 480, 255, 470,1,1,1)


def mouseListener(button,state,x,y):
    global canyon_top,c,b,cl,sky,clouds,gameover,fuel_level,game_state,fuel_cans,immunity_cans,is_immune,immunity_time,immunity_active,immunity_duration,pause_time,pause_start_time
    actualx = x
    actualy = 500 - y
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Check if the user clicked on the restart/back button
        if 240 <= actualx <= 270 and 470 <= actualy <= 490:
            canyon_top = [{"x": i, "y": random.randint(60, 100)} for i in range(0, 600, 20)]
            c = 0
            b = 0
            cl = 0
            sky = (0.53, 0.81, 0.92, 1)
            clouds = []
            gameover = False
            fuel_level = 100
            game_state="Playing"
            # powerups array
            fuel_cans = []
            immunity_cans = []
            is_immune = False 
            immunity_time = 0  # Starts at 0
            immunity_active = False  # Initially not active
            immunity_duration = 15 # Immunity lasts 5 seconds
            print("starting over")
            glutPostRedisplay()
        # Check if the user clicked on the pause/resume button
        elif 300 <= actualx <= 320 and 470 <= actualy <= 490:
            if game_state == "Playing":
                game_state = "Paused"
                print("Game Paused")
                pause_start_time=time.time()
            elif game_state == "Paused":
                game_state = "Playing"
                print("Game Resumed")
                pause_time += time.time() - pause_start_time
            glutPostRedisplay()  

        # Check if the user clicked on the close button
        elif 350 <= actualx <= 370 and 470 <= actualy <= 490: 
            glutLeaveMainLoop()

# ----end of button related code----

def specialKeyListener(key, x, y):
    global b, fuel_level, gameover
    b1 = balloon_hitbox(b)
    if fuel_level <= 0:
        gameover = True
        return
    if key == GLUT_KEY_UP and b1.ymax < 500:
        b += 10
        fuel_level = max(0, fuel_level - 0.5)

    if key == GLUT_KEY_DOWN:
        b -= 10
        fuel_level = max(0, fuel_level - 0.5)

    glutPostRedisplay()


def animation():
    global gameover, b, slow, slowmo, game_state
    if not gameover and game_state == "Playing":
        update_canyon_top()
        move_clouds()
        move_slow(slow)
        check_planes()
        update_planes()
        b -= 1  # gravity
    glutPostRedisplay()


def iterate():
    glViewport(0, 0, 600, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 600, 0.0, 500, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


# print("-----SLOW ARRAY-----", slow)


# ----Main function----
def showScreen():
    global c, b, gameover, slow, print_score, fuel_level, game_state, pause_time
    glClearColor(*sky)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glColor3f(1.0, 1.0, 0.0)
    if not gameover:
        balloons(b)
        draw_canyon_top()
        if game_state == "Playing":
            cloud()
        draw_clouds()

        # fuel display
        fuel_bar()
        fuel_powerup()
        draw_fuel_cans()

        # bird display
        generate_birds()
        draw_birds()

        # aeroplane display
        drawAeroplane()

        ####check airplane balloon collision
        if check_airplane_balloon_collision():
            gameover = True
            print("Collided with plane!")

        if fuel_can_collision() == True:
            print("Collided with fuel can!")
            fuel_level = min(100, fuel_level + 10)
            fuel_cans.pop()

        if check_bird_collision() == True:
            print("Collided with bird!")
            gameover = True
        if (
            random.randint(1, 100) == 77 and len(slow) == 0 and not slowmo
        ):  # slow motion circles will generate
            slow_motion()
        if check_collision_with_canyon() == True:
            gameover = True
        if len(clouds) != 0:
            if cloud_collision() == True:
                print("Collided with cloud!")
                gameover = True
        if len(slow) != 0:
            i = slow[0]
            if slow[0][1] <= 0:
                slow = []
            else:
                circle(i[0], i[3], i[4], i[5], i[1], i[2])
        if collide_slowmo(slow) == True:
            slow = []
            activate_slow_mo()
        if slowmo == True:
            update_slow_mo()

        if game_state == "Paused":
            resume()  
        else:
            pause()  
        close()
        back()

    if gameover and print_score:
        print("Your score is " + str(round(time.time() - start_time - pause_time)))
        print_score = False
    glutSwapBuffers()


glutInit()

# need to refactor this
planes_initVal()

glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(600, 500)  # window size
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"Up And Away!")  # window name
glutDisplayFunc(showScreen)
glutIdleFunc(animation)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)
glutMainLoop()
