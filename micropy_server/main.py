#!/usr/bin/env pybricks-micropython
import socket
import time
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop

ev3 = EV3Brick()
ev3.speaker.beep()

motor_A = Motor(Port.A)
#motor_B = Motor(Port.B)

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



def cmd_sense_query(cmd, data):
    print("Received sense query", data)
    return "42"

commands = {'m1': cmd_motor1, 'm2': cmd_motor2, "sq":cmd_sense_query}


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
        client_socket.close()
        print("Client disconnected")

def start_server(host='0.0.0.0', port=1234):
    addr = socket.getaddrinfo(host, port)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print("Listening on", addr)

    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        handle_client(cl)

# Start the server
start_server()