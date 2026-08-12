#!/usr/bin/env python3
import asyncio
import os
import re
import sys
from dotenv import load_dotenv

load_dotenv()

from mud_client import MUDClient
from google.adk.agents import LlmAgent

# Factory to bind user-specific credentials to the tool
def make_execute_mud_commands(user: str, password: str):
    def execute_mud_commands(commands: str) -> str:
        """
        Executes a MUD command or a comma-separated list of commands in the MUD server.
        Args:
            commands: A string of MUD commands (e.g. "look" or "score")
        Returns:
            The command output from the MUD server.
        """
        print(f"\n[ADK Tool ({user})] Executing MUD command(s): {commands}")
        client = MUDClient()
        success, login_log = client.login(username=user, password=password)
        if not success:
            return f"Failed to log in: {login_log}"
        
        cmd_list = [c.strip() for c in commands.split(",") if c.strip()]
        res = client.execute_commands(cmd_list)
        client.close()
        
        output = ""
        for r in res.get("results", []):
            output += f"=== {r['command']} ===\n{r['output']}\n\n"
        return output
    return execute_mud_commands

def parse_agent_md() -> dict:
    """Parses agent.md to extract the name, description, and instructions."""
    agent_md_path = "agent.md"
    with open(agent_md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not frontmatter_match:
        raise ValueError("Could not parse agent.md YAML frontmatter")
    
    fm_text, instructions = frontmatter_match.groups()
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
            
    return {
        "name": fm.get("name", "tbamud-player"),
        "description": fm.get("description", ""),
        "instruction": instructions.strip()
    }

async def run_single_agent(user: str, password: str, prompt: str):
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    agent_info = parse_agent_md()
    
    # Instantiate the LlmAgent with a user-specific tool
    tool = make_execute_mud_commands(user, password)
    agent = LlmAgent(
        model="gemini-3.5-flash",
        name=f"{agent_info['name']}_{user}".replace("-", "_"),
        instruction=agent_info["instruction"],
        tools=[tool]
    )
    
    # Set up InMemoryRunner
    runner = InMemoryRunner(agent=agent, app_name=f"tbamud_player_{user}")
    
    # Create the session (required by InMemoryRunner)
    session_id = f"tbamud_session_{user}"
    await runner.session_service.create_session(
        app_name=f"tbamud_player_{user}",
        user_id=user,
        session_id=session_id
    )
    
    # Construct types.Content message
    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    
    # Run the agent and process output events
    async for event in runner.run_async(user_id=user, session_id=session_id, new_message=msg):
        if getattr(event, "error_message", None):
            print(f"\n[Error - {user}] {event.error_message}", file=sys.stderr)
            break
            
        content = getattr(event, "content", None) or getattr(event, "output", None)
        if content and hasattr(content, "parts"):
            for part in content.parts:
                if hasattr(part, "text") and part.text:
                    # Prefix each output line to make concurrent stdout distinct
                    lines = part.text.splitlines()
                    for line in lines:
                        print(f"[{user}] {line}")

async def main():
    prompt_dummy = (
        "You are logged in as 'dummy'. Run the 'score' command in the MUD to check "
        "your character's status (including hunger, thirst, or other vitals). "
        "Report back whether you are hungry or thirsty."
    )
    prompt_smarty = (
        "You are logged in as 'smarty'. Run the 'score' command in the MUD to check "
        "your character's status (including hunger, thirst, or other vitals). "
        "Report back whether you are hungry or thirsty."
    )
    
    print("[+] Launching both agents concurrently...")
    await asyncio.gather(
        run_single_agent("dummy", "helloworld", prompt_dummy),
        run_single_agent("smarty", "goodbyemoon", prompt_smarty)
    )
    print("[+] Concurrent execution completed.")

if __name__ == "__main__":
    asyncio.run(main())
