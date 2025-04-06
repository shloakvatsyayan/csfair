import time

class PIDController:

    def __init__(self, Kp=1.2, Ki=0.0, Kd=0.3):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.prev_error = 0
        self.integral = 0
        self.last_time = time.time()

    def compute(self, error, dt):
        if dt == 0:
            return 0
        P = self.Kp * error
        self.integral += error * dt
        I = self.Ki * self.integral
        derivative = (error - self.prev_error) / dt
        D = self.Kd * derivative
        self.prev_error = error
        return P + I + D

class FaceTrackerPIDController:
    OUTPUT_MIN = -100
    OUTPUT_MAX = 100

    def __init__(self,   x_pid_controller, y_pid_controller, min_error=10):
        self.x_pid_controller = x_pid_controller
        self.y_pid_controller = y_pid_controller
        self.min_error = min_error
        self.last_time = time.time()


    def process(self, x1, y1, x2, y2 , frame_w, frame_h):
        """
        you can get frame_w and frame_h from frame.shape object
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param frame_w:
        :param frame_h:
        :return:
        """
        # Calculate the center of the frame
        center_x = frame_w // 2
        center_y = frame_h // 4

        # Calculate the error
        error_x = center_x - ((x1 + x2) // 2)
        error_y = center_y - ((y1 + y2) // 2)

        # Calculate the time difference
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        # Compute PID output for both axes
        output_x = self.x_pid_controller.compute(error_x, dt)
        output_y = self.y_pid_controller.compute(error_y, dt)

        # Clamp the output to the defined range
        output_x = max(self.OUTPUT_MIN, min(self.OUTPUT_MAX, output_x))
        output_y = max(self.OUTPUT_MIN, min(self.OUTPUT_MAX, output_y))

        output_x = int(output_x) if abs(output_x) > self.min_error else 0
        output_y = int(output_y) if abs(output_y) > self.min_error else 0
        return output_x, output_y

    @staticmethod
    def create_face_tracker_pid_controller(x_tuple, y_tuple, min_error=10):
        x_pid = PIDController(Kp=x_tuple[0], Ki=x_tuple[1], Kd=x_tuple[2])
        y_pid = PIDController(Kp=y_tuple[0], Ki=y_tuple[1], Kd=y_tuple[2])
        return FaceTrackerPIDController(x_pid, y_pid, min_error)


