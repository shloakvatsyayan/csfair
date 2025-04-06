"""
Click on a person to keep tracking that person until they walk off camera.
Click on a different person to start tracking them instead, or click anywhere else (not a person) to stop tracking somone.
"""
import cv2
from ultralytics import YOLO
import objtracking.test_tracking as tracking

SPORTS_BALL = "sports ball"
CAR = "car"
class_to_track = CAR
model = YOLO("models/yolo11n.pt")
model.to("cuda")  # comment this line out if not using an nvidia gpu

print("Starting video capture...")
camera_stream = cv2.VideoCapture(3)
#camera_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#camera_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

frame_processor = tracking.FrameProcessor(class_to_track)

cv2.namedWindow("Webcam")
cv2.setMouseCallback("Webcam", frame_processor.handle_mouse_click)

print("Press 'q' to quit, started")

while True:
    try:
        ret, frame = camera_stream.read()
        if not ret:
            break

        frame_processor.process_frame(frame=frame, model=model)

        cv2.imshow("Webcam", frame)
        key_pressed = cv2.waitKey(1)
        if key_pressed & 0xFF == ord('q'):
            break
    except KeyboardInterrupt:
        break

camera_stream.release()
cv2.destroyAllWindows()