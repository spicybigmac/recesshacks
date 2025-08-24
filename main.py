import cv2
import mediapipe as mp
import sys
import os
import tkinter.filedialog

# ai init
mphands = mp.solutions.hands
mpdrawing = mp.solutions.drawing_utils
hands = mphands.Hands(max_num_hands=2)

print("done loading ai")

# webcam stuff
if (sys.platform == "darwin" or sys.platform == "linux"):
    cap = cv2.VideoCapture(0)
elif (sys.platform == "win32"):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    

if not cap.isOpened():
    print("bad")
    exit()

WIDTH = 1280
HEIGHT = 720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)  
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

edges = [(0,1),(0,5),(0,17),(1,2),(2,3),(3,4),(5,9),(5,6),(6,7),(7,8),(9,13),(9,10),(10,11),(11,12),(13,17),(13,14),(14,15),(15,16),(17,18),(18,19),(19,20)]

# ------ VARIABLES FOR CUSTOMIZATION -------
windowname = "finger"
# everythings in BGR btw not RGB
handcolors = [
    ((255, 255, 0), (0, 0, 0)),
    ((6, 6, 50), (255, 255, 255)),
    ((6, 6, 50), (255, 255, 255)),
    ((255, 255, 0), (0, 0, 0)),
]
pointcolor = (0,255,0)
textcolor = (0,0,0)
linecolor = (0,255,0)
distance = 50

pointsbruh = [(0,0,0,0),(WIDTH,0,0,0),(0,HEIGHT,0,0),(WIDTH,HEIGHT,0,0)]
import random
for i in range(10):
    pointsbruh.append([random.randint(0,WIDTH),random.randint(0,HEIGHT),random.uniform(-1,1),random.uniform(-1,1)])

# LOADING MAP
MAPS = {}

def preprocess(turn):
    instruction,*tokens = turn.split("\n")

    if instruction == "-": instruction = ""

    requirements = [list(map(float,x.split())) for x in tokens]

    return instruction,requirements

def loadmaps():
    for mappath in os.listdir("maps"):
        mapname, extension = os.path.splitext(mappath)

        if extension == ".sys":
            *turns, = map(preprocess,open(f"maps/{mappath}", "r").read().split("\n\n"))
            MAPS[mapname] = turns

curmap = ""
currturn = 0

import pygame
pygame.init()

fonts = [pygame.font.Font("pixelmix.ttf",x) for x in range(101)]

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption(windowname)
clock = pygame.time.Clock()

SCENE = "menu"

palette = [(0,0,0),(255,0,0),(0,255,0),(0,0,255),(255,255,255)]

def ihateyou(x,y,rect):
    return rect[0] <= x <= rect[0]+rect[2] and rect[1] <= y <= rect[1]+rect[3]

frames = 100
currframes = frames

running = True
while running:
    success, frame = cap.read()
    if not success:
        break

    # mirror cuz non mirror is freaky
    frame = cv2.flip(frame,1)
    # ai processing
    rgbframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgbframe)

    dt = clock.tick(120)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(palette[0])

    # left,middle,right = pygame.mouse.get_pressed()
    # mx,my = pygame.mouse.get_pos()

    fingertipslists = [[],[],[]]
    if results.multi_hand_landmarks:
        handslist = [{},{},{}]
        for hand,keypoints in enumerate(results.multi_hand_landmarks):
            for i, landmark in enumerate(keypoints.landmark):
                if i in [4,8,12,16,20]:
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    fingertipslists[hand].append((cx,cy))

    keys = pygame.key.get_pressed()

    if SCENE == "menu":
        for i in range(4,len(pointsbruh)):
            point = pointsbruh[i]

            for fingertips in fingertipslists:
                for cx,cy in fingertips:
                    d2 = (cx-point[0])**2 + (cy-point[1])**2
                    if d2 > 0:
                        point[2] -= 40*(cx - point[0]) / d2
                        point[3] -= 40*(cy - point[1]) / d2

            for j in range(4,len(pointsbruh)):
                cx,cy = pointsbruh[j][0],pointsbruh[j][1]
                d2 = (cx-point[0])**2 + (cy-point[1])**2
                if d2 > 0:
                    point[2] -= 10*(cx - point[0]) / d2
                    point[3] -= 10*(cy - point[1]) / d2

            cx,cy = WIDTH/2, HEIGHT/2
            d2 = (cx-point[0])**2 + (cy-point[1])**2
            if d2 > 0:
                point[2] += 50*(cx - point[0]) / d2
                point[3] += 50*(cy - point[1]) / d2

                point[2] -= 50*(cy - point[1]) / d2
                point[3] += 50*(cx - point[0]) / d2

            point[2] *= 0.98
            point[3] *= 0.98

            if point[0] < 0:
                point[2] = abs(point[2])
            elif point[0] > WIDTH:
                point[2] = -abs(point[2])

            if point[1] < 0:
                point[3] = abs(point[3])
            elif point[1] > HEIGHT:
                point[3] = -abs(point[3])

            point[0] += point[2]
            point[1] += point[3]
            pygame.draw.circle(screen,(0,0,127),(point[0],point[1]),5)

        for i in range(len(pointsbruh)):
            for j in range(i+1,len(pointsbruh)):
                for k in range(j+1,len(pointsbruh)):
                    a = pointsbruh[i]
                    b = pointsbruh[j]
                    c = pointsbruh[k]

                    ax,ay,_,_ = a
                    bx,by,_,_ = b
                    cx,cy,_,_ = c

                    if (bx - ax)*(cy - ay)-(cx - ax)*(by - ay) < 0:
                        b,c = c,b
                        bx,by,cx,cy = cx,cy,bx,by

                    for l in range(len(pointsbruh)):
                        if l in [i,j,k]: continue

                        d = pointsbruh[l]
                        dx,dy,_,_ = d

                        ax_ = ax-dx
                        ay_ = ay-dy
                        bx_ = bx-dx
                        by_ = by-dy
                        cx_ = cx-dx
                        cy_ = cy-dy
                        if ((ax_*ax_ + ay_*ay_) * (bx_*cy_-cx_*by_) -
                            (bx_*bx_ + by_*by_) * (ax_*cy_-cx_*ay_) +
                            (cx_*cx_ + cy_*cy_) * (ax_*by_-bx_*ay_)) > 0:
                            break
                    else:
                        pygame.draw.lines(screen,(0,0,127),1,[(ax,ay),(bx,by),(cx,cy)],2)
                        
        title = fonts[100].render("Helping Hand", 1, palette[4])
        screen.blit(title,(WIDTH/2-title.get_width()/2,50))

        play = fonts[50].render("Play", 1, palette[4])
        rect = screen.blit(play,(WIDTH/2-play.get_width()/2-200,HEIGHT/2))
        rect = (rect[0]+rect[2]/2-150,rect[1]+rect[3]/2-50,300,100)
        pygame.draw.rect(screen,palette[4],rect,10)

        create = fonts[50].render("Create", 1, palette[4])
        rect2 = screen.blit(create,(WIDTH/2-create.get_width()/2+200,HEIGHT/2))
        rect2 = (rect2[0]+rect2[2]/2-150,rect2[1]+rect2[3]/2-50,300,100)
        pygame.draw.rect(screen,palette[4],rect2,10)

        if any(fingertips and all(ihateyou(cx,cy,rect) for cx,cy in fingertips) for fingertips in fingertipslists):
            SCENE = "mapselector"
            loadmaps()
        elif any(fingertips and all(ihateyou(cx,cy,rect2) for cx,cy in fingertips) for fingertips in fingertipslists):
            name = tkinter.filedialog.asksaveasfilename(defaultextension=".sys", filetypes=[("SYS files", "*.sys"), ("All files", "*.*")])
        
            if name:
                file = open(name,"w")
                file.truncate(0)
                SCENE = "mapcreator"

    elif SCENE == "mapselector":
        y = 10
        ystep = 100
        mxw = 0
        lnsz = fonts[50].get_linesize()

        for mapname in MAPS:
            text = fonts[50].render(mapname,1,(255,255,255))
            screen.blit(text,(10,y))
            y += ystep
            mxw = max(text.get_width(),mxw)

        y = 10
        for mapname in MAPS:
            rect = (10,y,mxw,lnsz)

            if any(fingertips and all(ihateyou(cx,cy,rect) for cx,cy in fingertips) for fingertips in fingertipslists):
                curmap = mapname
                currturn = 0
                SCENE = "map"
                break

            y += ystep

    elif SCENE == "mapcreator":
        if currframes == 0:
            if results.multi_hand_landmarks:
                file.write("-\n")

                for j,keypoints in enumerate(results.multi_hand_landmarks):
                    for i, landmark in enumerate(keypoints.landmark):
                        cx, cy = int(landmark.x * w), int(landmark.y * h)                
                        if (currframes == 0):
                            file.write(f"{j} {i} {cx/w} {cy/h}\n")
                
                file.write('\n')

            currframes = frames

        currframes -= 1
        cv2.putText(frame, str(currframes), (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 5, textcolor, 1, cv2.LINE_AA)

        surf = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1],"BGR")
        
        screen.blit(surf,(WIDTH/2-surf.get_width()/2,0))

    elif SCENE == "map":
        instruction, requirements = MAPS[curmap][currturn]
        pruned = [(x,y,z,w) for x,y,z,w in requirements if int(y) in [4,8,12,16,20,2,5,9,13,17,0]]

        if results.multi_hand_landmarks:
            fulfilled = [0 for _ in range(len(pruned))]
            for keypoints in results.multi_hand_landmarks:
                for i,(hand,a,xpos,ypos) in enumerate(pruned):
                    a = int(a)
                    if (abs(keypoints.landmark[a].x-xpos)*w <= distance and abs(keypoints.landmark[a].y-ypos)*h <= distance):
                        fulfilled[i] = 1

            if sum(fulfilled) == len(pruned):
                currturn += 1
                if currturn == len(MAPS[curmap]):
                    SCENE = "menu"

        handslist = [{},{},{}]
        for hand,num,x,y in requirements:
            center = (int(x*w),int(y*h))
            cv2.circle(frame, center=center, radius=5, color=pointcolor, thickness=2)
            cx, cy = int(x * w), int(y * h)
            # cv2.putText(frame, str(int(num)), (cx + 5, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, textcolor, 1, cv2.LINE_AA)

            handslist[int(hand)][num] = (int(x*w),int(y*h))
        for hand in handslist:
            for a,b in edges:
                if (a not in hand or b not in hand): continue
                cv2.line(frame, hand[a], hand[b], linecolor, 2)


        cv2.putText(frame,instruction,(10,h-10), cv2.FONT_HERSHEY_SIMPLEX, 1, textcolor, 1, cv2.LINE_AA)

        surf = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1],"BGR")
        
        screen.blit(surf,(WIDTH/2-surf.get_width()/2,0))

    if SCENE != "menu":
        play = fonts[30].render("Back", 1, palette[4])
        rect = screen.blit(play,(WIDTH-play.get_width()-60,HEIGHT-play.get_height()-30))
        rect = (rect[0]+rect[2]/2-100,rect[1]+rect[3]/2-40,200,80)
        pygame.draw.rect(screen,palette[4],rect,10)

        if any(fingertips and all(ihateyou(cx,cy,rect) for cx,cy in fingertips) for fingertips in fingertipslists):
            if SCENE == "mapcreator":
                file.close()

            SCENE = "menu"

    if results.multi_hand_landmarks:
        handslist = [{},{},{}]
        for hand,keypoints in enumerate(results.multi_hand_landmarks):
            for i, landmark in enumerate(keypoints.landmark):
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                handslist[hand][i] = (cx,cy)

        for hand in handslist:
            for a,b in edges:
                if (a not in hand or b not in hand): continue
                pygame.draw.line(screen,palette[1],hand[a],hand[b],10)

    pygame.display.flip()

cap.release()
pygame.quit()
