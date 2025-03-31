import cv2
from ultralytics import YOLO
import objtracking.tracking as tracking
from comms import SocketClient

class_to_track = "person"
model = YOLO("models/yolo11n.pt")
model.to("cuda")  # comment this line out if not using an nvidia gpu

print("Starting video capture, takes about 9 - 11 seconds to start")
camera_stream = cv2.VideoCapture(1)
camera_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
camera_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1000)

# Create a single client connection for the entire run.
client = SocketClient()

# Pass the client to the FrameProcessor.
frame_processor = tracking.FrameProcessor(class_to_track, socket_client=client)

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

# Cleanly close the socket connection when done.
client.close()