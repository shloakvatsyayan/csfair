import cv2
import time
import threading

YOLO_CLASS_NAMES = [
    "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
    "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "sofa", "pottedplant", "bed", "diningtable", "toilet", "tvmonitor", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
    "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]

direction_definitions = ["right", "left"]

YOLO_CLASS_IDX = {name: i for i, name in enumerate(YOLO_CLASS_NAMES)}


class FrameProcessor:
    def __init__(self, obj_class_name, socket_client, io_threshold_value=0.3):
        self.obj_class_name = obj_class_name
        self.iou_threshold_value = io_threshold_value
        self.current_tracked_box = None
        self.is_person_selected = False
        self.current_frame_boxes = []
        # Pass the socket_client to TrackingHandler.
        self.tracking_handler = TrackingHandler(socket_client)

    def set_current_frame_boxes(self, current_frame_boxes):
        self.current_frame_boxes = current_frame_boxes

    def track_person(self):
        if self.is_person_selected and self.current_tracked_box:
            best_iou_score = 0.0
            best_box_match = None
            for box in self.current_frame_boxes:
                iou_value = calculate_iou(self.current_tracked_box, box)
                if iou_value > best_iou_score:
                    best_iou_score = iou_value
                    best_box_match = box
            if best_box_match and best_iou_score >= self.iou_threshold_value:
                self.current_tracked_box = best_box_match
                self.tracking_handler.box_updated(self.obj_class_name, "")
            else:
                print("Lost track (no matching box over IOU threshold).")
                self.current_tracked_box = None
                self.is_person_selected = False

    def handle_mouse_click(self, event, mouse_x, mouse_y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            for (box_x1, box_y1, box_x2, box_y2) in self.current_frame_boxes:
                if box_x1 <= mouse_x <= box_x2 and box_y1 <= mouse_y <= box_y2:
                    self.current_tracked_box = (box_x1, box_y1, box_x2, box_y2)
                    self.is_person_selected = True
                    print("Selected new person for tracking:", self.current_tracked_box)
                    self.tracking_handler.tracking_started(self.obj_class_name, "", "", "")
                    return
            self.current_tracked_box = None
            self.is_person_selected = False
            print("No person clicked. Tracking disabled.")
            self.tracking_handler.tracking_stopped(self.obj_class_name, "")

    def process_frame(self, frame, model):
        current_frame_boxes = extract_frame_boxes(model, frame, self.obj_class_name)
        self.set_current_frame_boxes(current_frame_boxes)

        # track person
        self.track_person()

        # create boxes around detected people
        self.show_boxes(frame)

        # Offload command sending to a separate thread
        self.tracking_handler.turn_detection(self.is_person_selected, self.current_tracked_box, frame, print_output=True)

    def show_boxes(self, frame):
        for (box_x1, box_y1, box_x2, box_y2) in self.current_frame_boxes:
            rectangle_color = (255, 0, 255)
            rectangle_thickness = 2
            if (self.is_person_selected and self.current_tracked_box and (box_x1, box_y1, box_x2, box_y2) ==
                    self.current_tracked_box):
                rectangle_color = (0, 255, 0)
                rectangle_thickness = 3
            cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), rectangle_color, rectangle_thickness)

def calculate_iou(bounding_box_a, bounding_box_b):
    xA = max(bounding_box_a[0], bounding_box_b[0])
    yA = max(bounding_box_a[1], bounding_box_b[1])
    xB = min(bounding_box_a[2], bounding_box_b[2])
    yB = min(bounding_box_a[3], bounding_box_b[3])
    intersection_width = max(0, xB - xA)
    intersection_height = max(0, yB - yA)
    intersection_area = intersection_width * intersection_height
    area_a = (bounding_box_a[2] - bounding_box_a[0]) * (bounding_box_a[3] - bounding_box_a[1])
    area_b = (bounding_box_b[2] - bounding_box_b[0]) * (bounding_box_b[3] - bounding_box_b[1])
    return intersection_area / (area_a + area_b - intersection_area + 1e-6)


def get_class_idx(name):
    if name in YOLO_CLASS_IDX:
        return YOLO_CLASS_IDX[name]
    return -1


def extract_frame_boxes(model, frame, class_to_track):
    predictions = model.predict(source=frame, stream=True, verbose=False)
    current_frame_boxes = []
    for prediction in predictions:
        for bounding_box in prediction.boxes:
            if int(bounding_box.cls[0]) == get_class_idx(class_to_track):
                x1, y1, x2, y2 = map(int, bounding_box.xyxy[0])
                current_frame_boxes.append((x1, y1, x2, y2))
    return current_frame_boxes


class TrackingHandler:
    def __init__(self, socket_client):
        self.client = socket_client
        self.last_command_time = 0.0  # Track when the last command was sent

    def tracking_started(self, obj_class_name, bounding_box, mouse_x, moused_y):
        # Optionally log or handle when tracking starts.
        pass

    def tracking_stopped(self, obj_class_name, bounding_box):
        # Optionally log or handle when tracking stops.
        pass

    def box_updated(self, obj_class_name, bounding_box):
        # Optionally log or handle updates.
        pass

    def turn_detection(self, is_person_selected, current_tracked_box, frame, print_output=False):
        if is_person_selected and current_tracked_box:
            tracked_x1, tracked_y1, tracked_x2, tracked_y2 = current_tracked_box
            person_center_x = (tracked_x1 + tracked_x2) // 2
            frame_center_x = frame.shape[1] // 2

            # Calculate the error between the person center and frame center.
            error = person_center_x - frame_center_x

            # Gain factor to convert pixel difference to command value.
            gain = 0.05
            angular_speed = int(error * gain)

            # Ensure a minimum command magnitude if error is nonzero.
            if angular_speed != 0 and abs(angular_speed) < 10:
                angular_speed = 10 if angular_speed > 0 else -10

            command = f"m1 1000 {angular_speed}"

            # Throttle command sending: only send if 0.2s has passed since the last command.
            current_time = time.time()
            if current_time - self.last_command_time >= 0.2:
                self.last_command_time = current_time
                threading.Thread(target=self.send_command_async, args=(command, print_output), daemon=True).start()

    def send_command_async(self, command, print_output):
        start_time = time.time()
        response = self.client.send(command)
        end_time = time.time()
        delta = end_time - start_time
        print(f"Time: {delta:.2f}s")
        if print_output:
            print(response)