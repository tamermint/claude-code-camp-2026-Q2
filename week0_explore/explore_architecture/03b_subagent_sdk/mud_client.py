#!/usr/bin/env python3
"""
MUD Telnet Client Script for tbaMUD / CircleMUD
Handles telnet protocol negotiation, auto-login, command execution, ANSI stripping,
and clean prompt detection.
"""

import sys
import socket
import select
import re
import time
import json
import argparse
from typing import Tuple, List, Optional, Dict, Any

try:
    from state_manager import parse_and_update_state
except ImportError:
    try:
        from scripts.state_manager import parse_and_update_state
    except ImportError:
        parse_and_update_state = None

# Telnet Commands & Options (RFC 854)
IAC  = bytes([255])  # Interpret As Command
DONT = bytes([254])  # Don't perform option
DO   = bytes([253])  # Do perform option
WONT = bytes([252])  # Won't perform option
WILL = bytes([251])  # Will perform option
SB   = bytes([250])  # Subnegotiation Begin
SE   = bytes([240])  # Subnegotiation End

# Default target configuration
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 4000
DEFAULT_USER = "dummy"
DEFAULT_PASS = "helloworld"


class MUDClient:
    """Telnet client optimized for tbaMUD / CircleMUD text interfaces."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 5.0):
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
            print(f"[ERROR] Failed to connect to {self.host}:{self.port} - {e}", file=sys.stderr)
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
        """
        Process incoming raw bytes, filter IAC subnegotiations,
        and generate responses for basic option requests.
        Returns (clean_text_bytes, response_bytes).
        """
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
                            # Respond with WONT for any DO/DONT option requested by server
                            responses.extend(IAC + WONT + opt)
                            i += 3
                        else:
                            i += 2
                    elif cmd in (WILL, WONT):
                        if i + 2 < n:
                            opt = raw_bytes[i+2:i+3]
                            # Respond with DONT for any WILL/WONT option offered by server
                            responses.extend(IAC + DONT + opt)
                            i += 3
                        else:
                            i += 2
                    elif cmd == SB:
                        # Skip until SE (Subnegotiation End)
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
        """
        Read socket data until one of the match patterns is found or timeout occurs.
        """
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
                except Exception as e:
                    print(f"[ERROR] Socket read error: {e}", file=sys.stderr)
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

    def login(self, username: str = DEFAULT_USER, password: str = DEFAULT_PASS) -> Tuple[bool, str]:
        """
        Execute CircleMUD/tbaMUD login sequence.
        Returns (success_bool, transcript_string).
        """
        if not self.connect():
            return False, "Failed to connect to host."

        transcript = ""

        # Step 1: Wait for Name Prompt
        name_output = self.read_until([r"by what name", r"what name", r"login:", r"name:"], timeout=4.0)
        transcript += name_output

        if not name_output:
            return False, f"Did not receive login prompt. Received:\n{transcript}"

        # Step 2: Send Username
        self.send_line(username)
        time.sleep(0.5)

        # Step 3: Wait for Password Prompt
        pass_output = self.read_until([r"password:"], timeout=4.0)
        transcript += pass_output

        if "password:" not in pass_output.lower():
            # Might be asking if user is new or direct password
            pass_output += self.read_until([r"password:"], timeout=3.0)
            transcript += pass_output

        # Step 4: Send Password
        self.send_line(password)
        time.sleep(0.5)

        # Step 5: Handle MOTD / Welcome / Return key prompts & Main Menu
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

        # Check if in-game prompt (usually containing '>') is visible
        if ">" in transcript:
            return True, transcript
        else:
            return False, transcript

    def execute_commands(self, commands: List[str], delay: float = 0.5, strip_ansi: bool = True) -> Dict[str, Any]:
        """
        Execute a series of MUD commands and capture results.
        Returns detailed dict with command outputs.
        """
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

    def interactive_session(self, strip_ansi: bool = False):
        """Run an interactive session in terminal mode."""
        print(f"[INFO] Starting interactive session on {self.host}:{self.port} (Ctrl+C or 'quit' to exit)")
        import select

        try:
            while self.connected:
                r, _, _ = select.select([self.sock, sys.stdin], [], [], 0.1)
                for s in r:
                    if s == self.sock:
                        data = self.sock.recv(4096)
                        if not data:
                            print("\n[INFO] Connection closed by server.")
                            self.connected = False
                            break
                        clean_bytes, iac_reply = self._process_telnet_iac(data)
                        if iac_reply:
                            self.sock.sendall(iac_reply)
                        txt = clean_bytes.decode('utf-8', errors='ignore')
                        if strip_ansi:
                            txt = self.strip_ansi_codes(txt)
                        sys.stdout.write(txt)
                        sys.stdout.flush()
                    elif s == sys.stdin:
                        line = sys.stdin.readline()
                        if not line:
                            break
                        cmd = line.rstrip('\r\n')
                        self.send_line(cmd)
        except KeyboardInterrupt:
            print("\n[INFO] Session interrupted by user.")
        finally:
            self.close()


def main():
    parser = argparse.ArgumentParser(description="tbaMUD / CircleMUD Telnet Automation Client")
    parser.add_argument("--host", default=DEFAULT_HOST, help="MUD host address")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="MUD port number")
    parser.add_argument("--user", default=DEFAULT_USER, help="MUD username")
    parser.add_argument("--password", default=DEFAULT_PASS, help="MUD password")
    parser.add_argument("--cmd", help="Single command to execute after login")
    parser.add_argument("--cmds", help="Comma-separated commands to execute after login")
    parser.add_argument("--file", help="File containing list of commands to execute")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive session")
    parser.add_argument("--raw", action="store_true", help="Do not strip ANSI escape codes")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    strip_ansi = not args.raw

    client = MUDClient(host=args.host, port=args.port)
    success, login_log = client.login(username=args.user, password=args.password)

    if not success and not args.interactive:
        err_msg = f"Failed to log in to {args.host}:{args.port} as '{args.user}'. Log:\n{login_log}"
        if args.json:
            print(json.dumps({"success": False, "error": err_msg}))
        else:
            print(f"[ERROR] {err_msg}", file=sys.stderr)
        sys.exit(1)

    if args.interactive:
        client.interactive_session(strip_ansi=strip_ansi)
        return

    commands = []
    if args.cmd:
        commands.append(args.cmd)
    if args.cmds:
        commands.extend([c.strip() for c in args.cmds.split(',') if c.strip()])
    if args.file:
        try:
            with open(args.file, 'r') as f:
                commands.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])
        except Exception as e:
            print(f"[ERROR] Failed to read commands file: {e}", file=sys.stderr)
            sys.exit(1)

    if not commands:
        # Default status check if no command specified
        commands = ["look", "score", "inventory"]

    res = client.execute_commands(commands, strip_ansi=strip_ansi)
    client.close()

    if parse_and_update_state and res.get("success"):
        try:
            parse_and_update_state(res["results"], username=args.user)
        except Exception as e:
            print(f"[WARN] Failed to update state memory: {e}", file=sys.stderr)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        for r in res["results"]:
            print(f"=== Command: {r['command']} ===")
            print(r['output'])
            print()

if __name__ == "__main__":
    main()
