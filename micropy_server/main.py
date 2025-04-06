#!/usr/bin/env pybricks-micropython
import socket
import time
import sys
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop

ev3 = EV3Brick()
ev3.speaker.beep()

motor_A = Motor(Port.A)
motor_B = Motor(Port.B)

def cmd_motor1(cmd, data):
    values = data.split()
    if len(values) != 2:
        print("Invalid data for motor 1")
        return "R:400"
    try:
        speed = int(values[0])
        angle = int(values[1])
    except ValueError:
        print("Invalid data for motor 1")
        return "R:400"
    print("Received motor 1 with:\nSpeed: ", speed, "\nAngle: ", angle)
    motor_A.run_angle(speed, angle, then=Stop.HOLD, wait=True)
    return str(speed) + ", " + str(angle)

def cmd_motor2(cmd, data):
    values = data.split()
    if len(values) != 2:
        print("Invalid data for motor 2")
        return "R:400"
    try:
        speed = int(values[0])
        angle = int(values[1])
    except ValueError:
        print("Invalid data for motor 2")
        return "R:400"
    print("Received motor 2 with:\nSpeed: ", speed, "\nAngle: ", angle)
    motor_B.run_angle(speed, angle, then=Stop.HOLD, wait=True)
    return str(speed) + ", " + str(angle)


def cmd_dc_motor(cmd, data):
    args = data.split() 
    if len(args) != 2:
        print("Invalid data for DC motor 1")
        return "R:400"
    try:
        power_a = int(args[0])
        power_b = int(args[1])
        if power_a < -100 or power_a > 100 or power_b < -100 or power_b > 100:
            print("Invalid power")
            return "R:400"
        print("Received DC motor 1 with:\nPower A: ", power_a, "\nPower B: ", power_b)
        if power_a == 0:
            motor_A.stop()
        else:
            motor_A.dc(power_a)
        if power_b == 0:
            motor_B.stop()
        else:
            motor_B.dc(power_b)
        return str(power_a) + ", " + str(power_b)
    except ValueError:
        print("Invalid data for DC")
        return "R:400"

def cmd_dc_motor_stop(cmd, data):
    args = data.split()
    if len(args) != 1:
        print("Invalid data for DC motor stop")
        return "R:400"
    try:
        motor = args[0].strip().lower()
        if motor == "m1":
            motor_A.brake()
        elif motor == "m2":
            motor_B.brake()
        elif motor == "all":
            motor_A.brake()
            motor_B.brake()
        else:
            print("Invalid motor")
            return "R:400"
        print("Received DC motor stop with:\nMotor: ", motor)
        return "R:200"
    except ValueError:
        print("Invalid data for DC motor stop")
        return "R:400"


def cmd_sense_query(cmd, data):
    print("Received sense query", data)
    return "42"

commands = {'m1': cmd_motor1, 'm2': cmd_motor2, "sq":cmd_sense_query, 'dc': cmd_dc_motor, 'es': cmd_dc_motor_stop}


def process_line(line):
    print("Received from client:", line)
    if len(line) < 2:
        return "R:400"
    # the first two characters are the command, the rest is the data to process
    command = line[:2] # get the first two characters
    data = line[2:].strip() # get the rest of the line
    print("Command:["+str(command)+"]")
    print("Data:["+str(data)+"]")
    if command not in commands:
        return "R:410"
    command_fn = commands[command]
    response = command_fn(command, data)
    return "R:200 " + str(response)


def handle_client(client_socket):
    cl_file = client_socket.makefile('rwb', 0)
    try:
        while True:
            line = cl_file.readline()
            if not line:
                break
            decoded = line.decode('utf-8').strip()
            response = process_line(decoded) + "\n"
            client_socket.send(response.encode('utf-8'))
    except Exception as e:
        print("Error handling client:", e)
    finally:
        motor_A.stop()
        motor_B.stop()
        client_socket.close()
        print("Client disconnected")

def start_server(host='0.0.0.0', port=1234):
    addr = socket.getaddrinfo(host, port)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print("Listening on", addr)
    try:
        while True:
            cl, addr = s.accept()
            print('Client connected from', addr)
            handle_client(cl)
    except KeyboardInterrupt:
        print("Server stopped by user")
        s.close()
    except Exception as e:
        print("Error in server:", e)
        s.close()
    finally:
        s.close()
        print("Server closed")


# Start the server
start_server()
if __name__ == "__main__":
    # check if the script has a port number as an argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number, using default port 1234")
            port = 1234
    else:
        port = 1234
    start_server(host="0.0.0.0",port=port)