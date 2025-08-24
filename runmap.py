import cv2
import mediapipe as mp

# ai init
mphands = mp.solutions.hands
mpdrawing = mp.solutions.drawing_utils
hands = mphands.Hands(max_num_hands=2)

print("done loading ai")

# webcam stuff
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("bad")
    exit()
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
distance = 0.05

# LOADING MAP
mapname = "test"

f = [list(map(float, x.split())) for x in open(f"maps/{mapname}.txt", "r").read().split("\n")]
currturn = []
line = 0

def getnextturn():
    global line, currturn
    currturn = []
    while line < len(f) and f[line] != [-1]:
        currturn.append(f[line])
        line += 1
getnextturn()

while True:
    success, frame = cap.read()
    if success:
        # mirror cuz non mirror is freaky
        frame = cv2.flip(frame,1)
        # ai processing
        rgbframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgbframe)

        if results.multi_hand_landmarks:

            fulfilled = 0
            for i,keypoints in enumerate(results.multi_hand_landmarks):
                mpdrawing.draw_landmarks(frame, keypoints, mphands.HAND_CONNECTIONS,
                                         mpdrawing.DrawingSpec(color=handcolors[i][0], thickness=1, circle_radius=5),
                                         mpdrawing.DrawingSpec(color=handcolors[i][1], thickness=2, circle_radius=2))
                for i, landmark in enumerate(keypoints.landmark):
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    cv2.putText(frame, str(i), (cx + 5, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, textcolor, 1, cv2.LINE_AA)
                
                for a,xpos,ypos in currturn:
                    a = int(a)
                    if (abs(keypoints.landmark[a].x-xpos) <= distance and abs(keypoints.landmark[a].y-ypos) <= distance):
                        fulfilled += 1
            
            if (fulfilled == len(currturn)):
                getnextturn()
                if (len(currturn) == 0):
                    print("you did it")

        for num,x,y in currturn:
            center = (int(x*w),int(y*h))
            cv2.circle(frame, center=center, radius=10, color=pointcolor, thickness=3)
            cx, cy = int(x * w), int(y * h)
            cv2.putText(frame, str(int(num)), (cx + 5, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, textcolor, 1, cv2.LINE_AA)
        
        cv2.imshow(windowname, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()