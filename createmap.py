import cv2
import mediapipe as mp
import sys

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
frames = 50
currframes = frames

# LOADING MAP
mapname = "cutting2"
f = open(f"maps/{mapname}.sys", "w")

while True:
    success, frame = cap.read()
    if success:
        # mirror cuz non mirror is freaky
        frame = cv2.flip(frame,1)
        # ai processing
        rgbframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgbframe)

        if (currframes == 0):
            f.write("-\n")

        if results.multi_hand_landmarks:
            for j,keypoints in enumerate(results.multi_hand_landmarks):
                mpdrawing.draw_landmarks(frame, keypoints, mphands.HAND_CONNECTIONS,
                                         mpdrawing.DrawingSpec(color=handcolors[j][0], thickness=1, circle_radius=5),
                                         mpdrawing.DrawingSpec(color=handcolors[j][1], thickness=2, circle_radius=2))
                for i, landmark in enumerate(keypoints.landmark):
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    cv2.putText(frame, str(i), (cx + 5, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, textcolor, 1, cv2.LINE_AA)
                
                    if (currframes == 0):
                        f.write(f"{j} {i} {cx/w} {cy/h}\n")
        
        if (currframes == 0):
            f.write('\n')
            currframes = frames

        currframes -= 1
        cv2.putText(frame, str(currframes), (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 5, textcolor, 1, cv2.LINE_AA)

        cv2.imshow(windowname, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()