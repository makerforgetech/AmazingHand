
import cv2
import mediapipe as mp
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarker, HandLandmarkerOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
from mediapipe.tasks.python.vision.drawing_utils import draw_landmarks
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarksConnections
from mediapipe.tasks.python.vision.core.image import Image, ImageFormat
import numpy as np
import sys
import os

# Import robot hand control functions from AmazingHand_Demo.py
import time as _time
import numpy as _np
from rustypot import Scs0009PyController

# Robot hand control setup (from AmazingHand_Demo.py)
Side = 1  # 1=> Right Hand // 2=> Left Hand
MaxSpeed = 7
CloseSpeed = 3
MiddlePos = [1, -3, 0, 0, 0, -8, 0, 0]  # replace values by your calibration results

controller = None
try:
    controller = Scs0009PyController(
        serial_port="/dev/ttyACM0",
        baudrate=1000000,
        timeout=0.5,
    )
except Exception as e:
    # if error is 'no such file or directory', it means the hand is not connected
    if "No such file or directory" in str(e):
        print("Robot hand not detected. Please connect the hand and try again.")
        sys.exit()
    else:
        raise e

def Move_Index(Angle_1, Angle_2, Speed):
    controller.write_goal_speed(1, Speed)
    _time.sleep(0.0002)
    controller.write_goal_speed(2, Speed)
    _time.sleep(0.0002)
    Pos_1 = _np.deg2rad(MiddlePos[0] + Angle_1)
    Pos_2 = _np.deg2rad(MiddlePos[1] + Angle_2)
    controller.write_goal_position(1, Pos_1)
    controller.write_goal_position(2, Pos_2)
    _time.sleep(0.005)

def Move_Middle(Angle_1, Angle_2, Speed):
    controller.write_goal_speed(3, Speed)
    _time.sleep(0.0002)
    controller.write_goal_speed(4, Speed)
    _time.sleep(0.0002)
    Pos_1 = _np.deg2rad(MiddlePos[2] + Angle_1)
    Pos_2 = _np.deg2rad(MiddlePos[3] + Angle_2)
    controller.write_goal_position(3, Pos_1)
    controller.write_goal_position(4, Pos_2)
    _time.sleep(0.005)

def Move_Ring(Angle_1, Angle_2, Speed):
    controller.write_goal_speed(5, Speed)
    _time.sleep(0.0002)
    controller.write_goal_speed(6, Speed)
    _time.sleep(0.0002)
    Pos_1 = _np.deg2rad(MiddlePos[4] + Angle_1)
    Pos_2 = _np.deg2rad(MiddlePos[5] + Angle_2)
    controller.write_goal_position(5, Pos_1)
    controller.write_goal_position(6, Pos_2)
    _time.sleep(0.005)

def Move_Thumb(Angle_1, Angle_2, Speed):
    controller.write_goal_speed(7, Speed)
    _time.sleep(0.0002)
    controller.write_goal_speed(8, Speed)
    _time.sleep(0.0002)
    Pos_1 = _np.deg2rad(MiddlePos[6] + Angle_1)
    Pos_2 = _np.deg2rad(MiddlePos[7] + Angle_2)
    controller.write_goal_position(7, Pos_1)
    controller.write_goal_position(8, Pos_2)
    _time.sleep(0.005)

def OpenHand():
    Move_Index(-35, 35, MaxSpeed)
    Move_Middle(-35, 35, MaxSpeed)
    Move_Ring(-35, 35, MaxSpeed)
    Move_Thumb(-35, 35, MaxSpeed)

def CloseHand():
    Move_Index(90, -90, CloseSpeed)
    Move_Middle(90, -90, CloseSpeed)
    Move_Ring(90, -90, CloseSpeed)
    Move_Thumb(90, -90, CloseSpeed + 1)

def Scissors():
    # Victory pose, then alternate index/middle
    if Side == 1:  # Right Hand
        Move_Index(-15, 65, MaxSpeed)
        Move_Middle(-65, 15, MaxSpeed)
        Move_Ring(90, -90, MaxSpeed)
        Move_Thumb(90, -90, MaxSpeed)
        for _ in range(3):
            _time.sleep(0.2)
            Move_Index(-50, 20, MaxSpeed)
            Move_Middle(-20, 50, MaxSpeed)
            _time.sleep(0.2)
            Move_Index(-15, 65, MaxSpeed)
            Move_Middle(-65, 15, MaxSpeed)
    else:  # Left Hand
        Move_Index(-65, 15, MaxSpeed)
        Move_Middle(-15, 65, MaxSpeed)
        Move_Ring(90, -90, MaxSpeed)
        Move_Thumb(90, -90, MaxSpeed)
        for _ in range(3):
            _time.sleep(0.2)
            Move_Index(-20, 50, MaxSpeed)
            Move_Middle(-50, 20, MaxSpeed)
            _time.sleep(0.2)
            Move_Index(-65, 15, MaxSpeed)
            Move_Middle(-15, 65, MaxSpeed)

def move_hand_by_gesture(gesture):
    """
    Move the robot hand according to the detected gesture.
    gesture: str, one of 'Rock', 'Paper', 'Scissors'
    """
    if gesture == "Rock":
        OpenHand()
    elif gesture == "Paper":
        Scissors()
    elif gesture == "Scissors":
        CloseHand()


# Download the hand landmark model if not present
import urllib.request
MODEL_PATH = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("Downloading hand landmark model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

# Initialize the hand landmarker
options = HandLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionTaskRunningMode.VIDEO,
    num_hands=2
)
hand_landmarker = HandLandmarker.create_from_options(options)


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    sys.exit()

frame_idx = 0
last_prediction = None
while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Run hand landmark detection (VIDEO mode requires timestamp)
    mp_image = Image(image_format=ImageFormat.SRGB, data=frame_rgb)
    result = hand_landmarker.detect_for_video(mp_image, frame_idx)
    frame_idx += 1

    annotated_image = frame.copy()

    prediction_text = ""
    if result.hand_landmarks:
        for hand_landmarks in result.hand_landmarks:
            draw_landmarks(
                annotated_image,
                hand_landmarks,
                HandLandmarksConnections.HAND_CONNECTIONS
            )

            # Extract landmark coordinates
            lmList = []
            for id, lm in enumerate(hand_landmarks):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            # Rule-based RPS detection
            tips = [4, 8, 12, 16, 20]
            pip_joints = [3, 6, 10, 14, 18]
            fingers = []
            if lmList:
                if lmList[4][1] < lmList[3][1]:
                    fingers.append(1)  # Thumb open
                else:
                    fingers.append(0)  # Thumb closed
                for tip, pip in zip(tips[1:], pip_joints[1:]):
                    if lmList[tip][2] < lmList[pip][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                # Rule logic
                if fingers[1:] == [0, 0, 0, 0]:
                    prediction_text = "Rock"
                elif fingers[1:] == [1, 1, 1, 1]:
                    prediction_text = "Paper"
                elif fingers[1:3] == [1, 1] and fingers[3:] == [0, 0]:
                    prediction_text = "Scissors"
                else:
                    prediction_text = "Unknown"

                # Move robot hand if gesture changed
                if prediction_text in ("Rock", "Paper", "Scissors") and prediction_text != last_prediction:
                    move_hand_by_gesture(prediction_text)
                    last_prediction = prediction_text

            cv2.putText(annotated_image, f"Prediction: {prediction_text}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    cv2.imshow('Hand Recognition', annotated_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()