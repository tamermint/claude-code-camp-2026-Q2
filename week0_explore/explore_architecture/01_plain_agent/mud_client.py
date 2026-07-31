import socket
import time

class MudClient:
    def __init__(self, host="localhost", port=4000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        self.sock.connect((host, port))

    def _read_until(self, target):
        data = b""
        while target not in data:
            try:
                chunk = self.sock.recv(4096)
                if not chunk: break
                data += chunk
            except socket.timeout:
                break
        return data

    def login(self, username, password):
        self._read_until(b"By what name do you wish to be known?")
        self.sock.send(username.encode('ascii') + b"\r\n")
        
        self._read_until(b"Password:")
        self.sock.send(password.encode('ascii') + b"\r\n")
        
        # Read the MOTD and wait for return
        self._read_until(b"*** PRESS RETURN:")
        self.sock.send(b"\r\n")
        
        # Select "1" to enter the game
        self._read_until(b"Make your choice:")
        self.sock.send(b"1\r\n")
        time.sleep(2) # Wait for load

    def send_command(self, command):
        self.sock.send(command.encode('ascii') + b"\r\n")
        time.sleep(1)
        data = b""
        try:
            while True:
                chunk = self.sock.recv(4096)
                if not chunk: break
                data += chunk
        except socket.timeout:
            pass
        return data.decode('ascii', errors='ignore')
