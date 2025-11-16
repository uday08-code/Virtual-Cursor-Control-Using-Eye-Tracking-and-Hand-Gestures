import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

pyautogui.FAILSAFE = False
cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1,
                       min_detection_confidence=0.8, min_tracking_confidence=0.8)
draw = mp.solutions.drawing_utils

prev_x, prev_y = 0, 0
smooth = 7
click_thresh = 0.03
click_delay = 1
last_click_time = 0
click_count = 0
scroll_speed_factor = 100  # Reduced factor for better scroll control
prev_scroll_y = None
last_scroll_time = 0
scroll_delay = 0.05  # Reduced scroll delay
click_effect_time = 0
click_effect_duration = 0.2
click_pos = None

def distance(p1, p2):
    return np.linalg.norm(np.array([p1.x - p2.x, p1.y - p2.y]))

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    h, w, _ = frame.shape

    if result.multi_hand_landmarks:
        hand = result.multi_hand_landmarks[0]
        draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        lm = hand.landmark

        index_finger = lm[8]
        middle_finger = lm[12]
        thumb = lm[4]

        screen_x, screen_y = screen_w * index_finger.x, screen_h * index_finger.y
        curr_x = prev_x + (screen_x - prev_x) / smooth
        curr_y = prev_y + (screen_y - prev_y) / smooth
        pyautogui.moveTo(int(curr_x), int(curr_y))
        prev_x, prev_y = curr_x, curr_y

        if distance(index_finger, thumb) < click_thresh:
            if time.time() - last_click_time > 0.3:
                click_count += 1
                last_click_time = time.time()
                click_pos = (int(index_finger.x * w), int(index_finger.y * h))
                click_effect_time = time.time()
                if click_count == 1:
                    pyautogui.click()
                elif click_count == 2:
                    pyautogui.doubleClick()
                    click_count = 0
        else:
            if time.time() - last_click_time > click_delay:
                click_count = 0

        if distance(index_finger, middle_finger) < 0.05:  # Increased threshold for scrolling
            current_time = time.time()
            if prev_scroll_y is not None and current_time - last_scroll_time > scroll_delay:
                diff = index_finger.y - prev_scroll_y
                if abs(diff) > 0.002:  # Lower sensitivity threshold
                    scroll_amount = int(-diff * scroll_speed_factor)
                    pyautogui.scroll(scroll_amount)
                    last_scroll_time = current_time
            prev_scroll_y = index_finger.y
        else:
            prev_scroll_y = None

    if click_pos and time.time() - click_effect_time < click_effect_duration:
        cv2.circle(frame, click_pos, 20, (0, 255, 0), 3)

    cv2.imshow("Hand Control with Click + Double Click", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
