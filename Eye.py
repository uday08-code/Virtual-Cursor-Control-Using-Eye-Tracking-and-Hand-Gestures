import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np

# Initialize modules
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
screen_w, screen_h = pyautogui.size()

# Smoothing parameters
prev_x, prev_y = 0, 0
smoothing = 5  # Higher value = more smoothing

# Blink detection threshold
BLINK_THRESHOLD = 0.004
last_click_time = 0
click_delay = 1  # seconds

# FPS calculation
prev_frame_time = 0

while True:
    ret, frame = cam.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape

    if landmark_points:
        landmarks = landmark_points[0].landmark

        # Iris tracking for cursor movement
        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

            if id == 1:  # Use second iris point
                screen_x = screen_w / frame_w * x
                screen_y = screen_h / frame_h * y

                # Smooth movement
                curr_x = prev_x + (screen_x - prev_x) / smoothing
                curr_y = prev_y + (screen_y - prev_y) / smoothing
                pyautogui.moveTo(curr_x, curr_y)

                prev_x, prev_y = curr_x, curr_y

        # Blink detection (left eye)
        left_eye = [landmarks[145], landmarks[159]]
        for point in left_eye:
            x = int(point.x * frame_w)
            y = int(point.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)

        # Eye blink logic
        eye_distance = left_eye[0].y - left_eye[1].y
        current_time = time.time()
        if eye_distance < BLINK_THRESHOLD and (current_time - last_click_time) > click_delay:
            pyautogui.click()
            last_click_time = current_time

    # Show FPS
    new_frame_time = time.time()
    fps = int(1 / (new_frame_time - prev_frame_time + 1e-6))
    prev_frame_time = new_frame_time
    cv2.putText(frame, f'FPS: {fps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('Eye Controlled Mouse', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



# Cleanup
cam.release()
cv2.destroyAllWindows()
