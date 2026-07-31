import socket
import time
import re

class MudAgent:
    def __init__(self, host="localhost", port=4000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        self.sock.connect((host, port))

    def read_until(self, target):
        data = b""
        while target not in data:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            except socket.timeout:
                break
        return data.decode('ascii', errors='ignore')

    def read_until_prompt(self):
        data = b""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                if data.rstrip().endswith(b">"):
                    break
            except socket.timeout:
                break
        return data.decode('ascii', errors='ignore')

    def login(self, username, password):
        print("Logging in...")
        self.read_until(b"By what name do you wish to be known?")
        self.sock.send(username.encode('ascii') + b"\r\n")
        
        self.read_until(b"Password:")
        self.sock.send(password.encode('ascii') + b"\r\n")
        
        self.read_until(b"*** PRESS RETURN:")
        self.sock.send(b"\r\n")
        
        self.read_until(b"Make your choice:")
        self.sock.send(b"1\r\n")
        
        # Read initial entry screen up to prompt
        welcome = self.read_until_prompt()
        print("Logged in successfully!")
        return welcome

    def send_command(self, cmd):
        print(f"Sending command: {cmd}")
        self.sock.send(cmd.encode('ascii') + b"\r\n")
        response = self.read_until_prompt()
        return response

def main():
    agent = MudAgent()
    welcome = agent.login("dummy", "helloworld")
    print(welcome)
    
    # Let's send the commands to navigate to the Bakery
    # 3001 -> 3005 (south)
    # 3005 -> 3014 (south)
    # 3014 -> 3013 (west)
    # 3013 -> 3009 (north)
    
    steps = ["south", "south", "west", "north"]
    for step in steps:
        res = agent.send_command(step)
        print(res)
        
    # Now at the bakery, let's list the items
    menu = agent.send_command("list")
    print("\n--- BAKERY MENU ---")
    print(menu)
    print("-------------------")
    
    agent.sock.close()

if __name__ == "__main__":
    main()
