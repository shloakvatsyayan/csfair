# Regular Python Client
import socket
import socket
def run_client(host='192.168.137.3', port=1234):
    with socket.create_connection((host, port)) as sock:
        with sock.makefile('rwb') as f:
            while True:
                line = input("Send to server: ")
                if line.lower() in ['exit', 'quit']:
                    break
                f.write((line + '\n').encode('utf-8'))
                f.flush()
                response = f.readline().decode('utf-8').strip()
                print("Response from server:", response)

class SocketClient:
    def __init__(self, host='192.168.137.3', port=1234):
        self.host = host
        self.port = port
        self.sock = socket.create_connection((self.host, self.port))
        self.file = self.sock.makefile('rwb')

    def send(self, message: str) -> str:
        """Send a message to the server and return the response."""
        self.file.write((message + '\n').encode('utf-8'))
        self.file.flush()
        response = self.file.readline().decode('utf-8').strip()
        return response

    def close(self):
        """Cleanly close the connection."""
        self.file.close()
        self.sock.close()


if __name__ == "__main__":
    client = SocketClient()
    try:
        while True:
            line = input("Send to server: ")
            if line.lower() in ['exit', 'quit']:
                break
            response = client.send(line)
            print("Response from server:", response)
    finally:
        client.close()


#run_client()