import cv2
import mediapipe as mp
import sys
import os

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
distance = 60

# LOADING MAP
MAPS = {}

def preprocess(turn):
    instruction,*tokens = turn.split("\n")

    if instruction == "-": instruction = ""

    requirements = [list(map(float,x.split())) for x in tokens]

    return instruction,requirements

for mappath in os.listdir("maps"):
    mapname, extension = os.path.splitext(mappath)

    if extension == ".sys":
        *turns, = map(preprocess,open(f"maps/{mappath}", "r").read().split("\n\n"))
        MAPS[mapname] = turns

curmap = "aaaa"
currturn = 0

import pygame
pygame.init()

font = pygame.font.SysFont("Verdana",32)

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption(windowname)
clock = pygame.time.Clock()

SCENE = "menu"

running = True
while running:
    dt = clock.tick(120)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((0,0,0))

    if SCENE == "menu":
        y = 10
        mxw = 0
        lnsz = font.get_linesize()

        for mapname in MAPS:
            text = font.render(mapname,1,(255,255,255))
            screen.blit(text,(10,y))
            y += lnsz
            mxw = max(text.get_width(),mxw)

        left,middle,right = pygame.mouse.get_pressed()

        if left:
            mx,my = pygame.mouse.get_pos()
            if 10 <= mx <= 10+mxw:
                y = 10
                for mapname in MAPS:
                    if y <= my <= y+lnsz:
                        curmap = mapname
                        currturn = 0
                        SCENE = "map"
                        break

                    y += lnsz

    elif SCENE == "map":
        success, frame = cap.read()
        if not success:
            break

        # mirror cuz non mirror is freaky
        frame = cv2.flip(frame,1)
        # ai processing
        rgbframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgbframe)

        instruction, requirements = MAPS[curmap][currturn]

        if results.multi_hand_landmarks:
            fulfilled = 0
            for i,keypoints in enumerate(results.multi_hand_landmarks):
                mpdrawing.draw_landmarks(frame, keypoints, mphands.HAND_CONNECTIONS,
                                            mpdrawing.DrawingSpec(color=handcolors[i][0], thickness=1, circle_radius=5),
                                            mpdrawing.DrawingSpec(color=handcolors[i][1], thickness=2, circle_radius=2))
                
                for i, landmark in enumerate(keypoints.landmark):
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    cv2.putText(frame, str(i), (cx + 5, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, textcolor, 1, cv2.LINE_AA)

                for a,xpos,ypos in requirements:
                    a = int(a)
                    if (abs(keypoints.landmark[a].x-xpos)*w <= distance and abs(keypoints.landmark[a].y-ypos)*h <= distance):
                        fulfilled += 1
            
            if fulfilled == len(requirements):
                currturn += 1
                if currturn == len(MAPS[curmap]):
                    SCENE = "menu"

        for num,x,y in requirements:
            center = (int(x*w),int(y*h))
            cv2.circle(frame, center=center, radius=10, color=pointcolor, thickness=3)
            cx, cy = int(x * w), int(y * h)
            cv2.putText(frame, str(int(num)), (cx + 5, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, textcolor, 1, cv2.LINE_AA)

        cv2.putText(frame,instruction,(10,h-10), cv2.FONT_HERSHEY_SIMPLEX, 1, textcolor, 1, cv2.LINE_AA)

        surf = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1],"BGR")
        
        screen.blit(surf,(WIDTH/2-surf.get_width()/2,0))

    pygame.display.flip()

cap.release()
pygame.quit()
