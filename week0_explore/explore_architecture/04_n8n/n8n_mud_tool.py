import socket
import select
import re
import time
import json
from typing import Tuple, List, Optional, Dict, Any

# Telnet Commands & Options (RFC 854)
IAC  = bytes([255])  # Interpret As Command
DONT = bytes([254])  # Don't perform option
DO   = bytes([253])  # Do perform option
WONT = bytes([252])  # Won't perform option
WILL = bytes([251])  # Will perform option
SB   = bytes([250])  # Subnegotiation Begin
SE   = bytes([240])  # Subnegotiation End

class MUDClient:
    """Telnet client optimized for tbaMUD / CircleMUD text interfaces."""

    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock: Optional[socket.socket] = None
        self.connected = False

    def connect(self) -> bool:
        """Establish TCP connection to the MUD server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            return False

    def close(self):
        """Close socket connection."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        self.connected = False

    def _process_telnet_iac(self, raw_bytes: bytes) -> Tuple[bytes, bytes]:
        """Process incoming raw bytes, filter IAC subnegotiations, and generate responses."""
        clean_text = bytearray()
        responses = bytearray()
        i = 0
        n = len(raw_bytes)

        while i < n:
            if raw_bytes[i:i+1] == IAC:
                if i + 1 < n:
                    cmd = raw_bytes[i+1:i+2]
                    if cmd in (DO, DONT):
                        if i + 2 < n:
                            opt = raw_bytes[i+2:i+3]
                            responses.extend(IAC + WONT + opt)
                            i += 3
                        else:
                            i += 2
                    elif cmd in (WILL, WONT):
                        if i + 2 < n:
                            opt = raw_bytes[i+2:i+3]
                            responses.extend(IAC + DONT + opt)
                            i += 3
                        else:
                            i += 2
                    elif cmd == SB:
                        se_idx = raw_bytes.find(SE, i + 2)
                        if se_idx != -1:
                            i = se_idx + 1
                        else:
                            break
                    else:
                        i += 2
                else:
                    i += 1
            else:
                clean_text.append(raw_bytes[i])
                i += 1

        return bytes(clean_text), bytes(responses)

    def read_until(self, match_patterns: List[str], timeout: float = 3.0, strip_ansi: bool = True) -> str:
        """Read socket data until one of the match patterns is found or timeout occurs."""
        if not self.sock or not self.connected:
            return ""

        buffer = ""
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            r, _, _ = select.select([self.sock], [], [], 0.2)
            if r:
                try:
                    data = self.sock.recv(4096)
                    if not data:
                        self.connected = False
                        break
                    
                    clean_bytes, iac_reply = self._process_telnet_iac(data)
                    if iac_reply:
                        self.sock.sendall(iac_reply)

                    text = clean_bytes.decode('utf-8', errors='ignore')
                    buffer += text

                    check_buf = self.strip_ansi_codes(buffer) if strip_ansi else buffer
                    for pat in match_patterns:
                        if re.search(pat, check_buf, re.IGNORECASE):
                            return buffer
                except socket.timeout:
                    break
                except Exception:
                    break

        return buffer

    def send_line(self, line: str):
        """Send a line of text terminated with CRLF."""
        if self.sock and self.connected:
            full_line = f"{line}\r\n"
            self.sock.sendall(full_line.encode('utf-8'))

    @staticmethod
    def strip_ansi_codes(text: str) -> str:
        """Remove ANSI control sequences from text."""
        ansi_regex = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\([a-zA-Z]|\x1b\][^\x07]*\x07')
        return ansi_regex.sub('', text)

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Execute CircleMUD/tbaMUD login sequence."""
        if not self.connect():
            return False, "Failed to connect to host."

        transcript = ""

        # Step 1: Wait for Name Prompt
        name_output = self.read_until([r"by what name", r"what name", r"login:", r"name:"], timeout=4.0)
        transcript += name_output
        if not name_output:
            return False, f"Did not receive login prompt. Log:\n{transcript}"

        # Step 2: Send Username
        self.send_line(username)
        time.sleep(0.5)

        # Step 3: Wait for Password Prompt
        pass_output = self.read_until([r"password:"], timeout=4.0)
        transcript += pass_output

        if "password:" not in pass_output.lower():
            pass_output += self.read_until([r"password:"], timeout=3.0)
            transcript += pass_output

        # Step 4: Send Password
        self.send_line(password)
        time.sleep(0.5)

        # Step 5: Handle Welcome / Menu
        post_pass = self.read_until([r"press return", r"hit return", r"press enter", r"\[return\]", r"make your choice", r">"], timeout=4.0)
        transcript += post_pass

        if re.search(r"press return|hit return|press enter|\[return\]", post_pass, re.IGNORECASE):
            self.send_line("")
            time.sleep(0.5)
            menu_output = self.read_until([r"make your choice", r">"], timeout=4.0)
            transcript += menu_output
            if re.search(r"make your choice", menu_output, re.IGNORECASE):
                self.send_line("1")
                time.sleep(0.5)
                in_game_output = self.read_until([r">"], timeout=4.0)
                transcript += in_game_output
        elif re.search(r"make your choice", post_pass, re.IGNORECASE):
            self.send_line("1")
            time.sleep(0.5)
            in_game_output = self.read_until([r">"], timeout=4.0)
            transcript += in_game_output

        if ">" in transcript:
            return True, transcript
        return False, transcript

    def execute_commands(self, commands: List[str], delay: float = 0.5, strip_ansi: bool = True) -> Dict[str, Any]:
        """Execute a series of MUD commands and capture results."""
        results = []
        full_raw = ""

        for cmd in commands:
            self.send_line(cmd)
            time.sleep(delay)
            out = self.read_until([r">"], timeout=3.0, strip_ansi=strip_ansi)
            full_raw += out
            clean_out = self.strip_ansi_codes(out) if strip_ansi else out
            results.append({
                "command": cmd,
                "output": clean_out.strip()
            })

        return {
            "success": True,
            "results": results,
            "raw_output": self.strip_ansi_codes(full_raw) if strip_ansi else full_raw
        }

def run_n8n_tool(query_str: str) -> Dict[str, Any]:
    # 1. Parse parameters from the query string passed by the n8n AI Agent
    try:
        params = json.loads(query_str)
    except Exception:
        # Fallback to raw text command if query is not JSON
        params = {"command": query_str}

    # 2. Extract configuration & inputs with sensible defaults
    host = params.get("host", "127.0.0.1")
    port = int(params.get("port", 4000))
    user = params.get("user", "dummy")
    password = params.get("password", "helloworld")
    
    commands = []
    if "commands" in params:
        if isinstance(params["commands"], list):
            commands = params["commands"]
        elif isinstance(params["commands"], str):
            commands = [c.strip() for c in params["commands"].split(",") if c.strip()]
    elif "command" in params:
        commands = [params["command"]]
    
    if not commands:
        commands = ["look"]

    # 3. Instantiate client
    client = MUDClient(host=host, port=port)
    
    # 4. Login
    login_success, login_log = client.login(username=user, password=password)
    if not login_success:
        client.close()
        return {
            "success": False,
            "error": f"Failed to login to MUD at {host}:{port} as {user}.",
            "login_log": MUDClient.strip_ansi_codes(login_log)
        }
    
    # 5. Execute commands
    try:
        result = client.execute_commands(commands)
    except Exception as e:
        result = {
            "success": False,
            "error": f"Error executing commands: {str(e)}"
        }
    finally:
        client.close()
        
    return result

# Return execution results to n8n AI Agent tool environment
return run_n8n_tool(query)
