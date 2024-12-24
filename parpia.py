from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
# end of imports
canyon_top = [{"x": i, "y": random.randint(60, 100)} for i in range(0, 600, 20)]
c = 0
b = 0
cl = 0
sky = (0.53, 0.81, 0.92, 1)
clouds = []
gameover = False
slowmo = False
slow = []
s = 0
slowmo_start_time = None
start_time = time.time()
print_score=True

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
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius**2:  # Check if the point is inside the circle
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
    y=random.randint(90,400) #cloud's vertical position will be generated randomly
    if len(clouds)==0 and random.randint(1,200)==10:
        clouds.append([25,0.69,0.74,0.71,530,y])
        clouds.append([25,0.69,0.74,0.71,550,y])
        clouds.append([25,0.69,0.74,0.71,580,y])
        clouds.append([25,0.69,0.74,0.71,550,y+20])

class cloud_hitbox:
    def __init__(self, arr, cl):
        self.xmin = arr[0][4]-arr[0][0]+cl
        self.ymin = arr[0][5]-arr[0][0]
        self.xmax = arr[2][4]+arr[2][0]+cl
        self.ymax = arr[3][5]+arr[3][0]
        self.height = self.ymax - self.ymin
        self.width = self.xmax - self.xmin

def draw_clouds():
    global clouds,cl
    if len(clouds)!=0:
        for i in range(0,len(clouds)-1,4):
            if clouds[0][4]-clouds[0][0]+cl<=0: #checking whether cloud has travelled to leftmost corner of screeen
                clouds=[]
            else:
                circle(clouds[i][0],clouds[i][1],clouds[i][2],clouds[i][3],clouds[i][4]+cl,clouds[i][5])
                circle(clouds[i+1][0],clouds[i+1][1],clouds[i+1][2],clouds[i+1][3],clouds[i+1][4]+cl,clouds[i+1][5])
                circle(clouds[i+2][0],clouds[i+2][1],clouds[i+2][2],clouds[i+2][3],clouds[i+2][4]+cl,clouds[i+2][5])
                circle(clouds[i+3][0],clouds[i+3][1],clouds[i+3][2],clouds[i+3][3],clouds[i+3][4]+cl,clouds[i+3][5])

                fill_circle_with_points(clouds[i][4]+cl,clouds[i][5], clouds[i][0], clouds[i][1],clouds[i][2],clouds[i][3])
                fill_circle_with_points(clouds[i+1][4]+cl,clouds[i+1][5], clouds[i+1][0], clouds[i+1][1],clouds[i+1][2],clouds[i+1][3])
                fill_circle_with_points(clouds[i+2][4]+cl,clouds[i+2][5], clouds[i+2][0], clouds[i+2][1],clouds[i+2][2],clouds[i+2][3])
                fill_circle_with_points(clouds[i+3][4]+cl,clouds[i+3][5], clouds[i+3][0], clouds[i+3][1],clouds[i+3][2],clouds[i+3][3])

def move_clouds():
    global cl,clouds,s
    if len(clouds)==0:
        cl=0
    else:
        cl=cl-(10-s)   # s is the variable which is actiavted when slowmode is on, so clouds will move slowly

def check_collision():

    balloon = balloon_hitbox(b)
    for i in range(len(canyon_top) - 1):
        current_point = canyon_top[i]
        next_point = canyon_top[i + 1]
        
        # Check if balloon is within the x-range of these canyon points
        if (balloon.xmin <= next_point["x"] and balloon.xmax >= current_point["x"]):
            if balloon.ymin <= current_point["y"]:
                print("Collided with canyon!")
                return True
    
    return False

def cloud_collision():
    global clouds,cl
    bb = balloon_hitbox(b)
    cc = cloud_hitbox(clouds,cl)
    return (bb.xmin)<(cc.xmin+cc.width) and (bb.xmin+bb.width)>(cc.xmin) and (bb.ymin)<(cc.ymin+cc.height) and (bb.ymin+bb.height)>(cc.ymin)

def slow_motion():
    global slow
    if not gameover:
        a = random.randint(90,400) 
        slow.append([14,600,random.randint(90,400),1,1,0])

def move_slow(arr):  #falling motion of slow
    if not gameover:
        for i in range(len(arr)): 
            if arr[i][1] > 0:
                arr[i][1] -= 5

def collide_slowmo(arr):
    if len(arr)!=0:
        balloon = balloon_hitbox(b)
        cxmin=arr[0][1]-arr[0][0]
        cymin=arr[0][2]-arr[0][0]
        cwidth,cheight=(2 * arr[0][0], 2 * arr[0][0])
        return (balloon.xmin)<(cxmin+cwidth) and (balloon.xmin+balloon.width)>(cxmin) and (balloon.ymin)<(cymin+cheight) and (balloon.ymin+balloon.height)>(cymin)

def activate_slow_mo():
    global slowmo, slowmo_start_time,s
    slowmo = True
    slowmo_start_time = time.time()
    s=5
    print("Slow motion activated!")

def update_slow_mo():
    global slowmo, slowmo_start_time,s
    if slowmo and (time.time() - slowmo_start_time >= 5):
        slowmo = False
        s=0
        print("Slow motion deactivated!")


def specialKeyListener(key, x, y):
    global b
    b1=balloon_hitbox(b)
    if key == GLUT_KEY_UP and b1.ymax<500:
        b += 10
    if key == GLUT_KEY_DOWN:
        b -= 10
    glutPostRedisplay()


def animation():
    global gameover,b,slow,slowmo
    if not gameover:
        update_canyon_top()
        move_clouds()
        move_slow(slow)
        b-=1 #gravity
    glutPostRedisplay()

def iterate():
    glViewport(0, 0, 600, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 600, 0.0, 500, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    global c, b, gameover, slow, print_score
    glClearColor(*sky)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glColor3f(1.0, 1.0, 0.0)
    if not gameover:
        balloons(b)
        draw_canyon_top()
        cloud()
        draw_clouds()
        if random.randint(1,1000)==77 and len(slow)==0 and not slowmo: #slow motion circles will generate
            slow_motion()
        if check_collision() == True:
            gameover = True
        if len(clouds)!=0:
            if cloud_collision() == True:
                print("Collided with cloud!")
                gameover = True
        if len(slow)!=0:
            for i in slow:
                if i!=None:
                    circle(i[0],i[3],i[4],i[5],i[1],i[2])
        if collide_slowmo(slow)==True:
            slow=[]
            activate_slow_mo()
        if slowmo==True:
            update_slow_mo()
            
    if gameover and print_score:
        print(time.time()-start_time)
        print_score=False
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
