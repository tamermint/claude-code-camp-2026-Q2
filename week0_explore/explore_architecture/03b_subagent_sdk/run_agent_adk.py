#!/usr/bin/env python3
import asyncio
import os
import re
import sys
from dotenv import load_dotenv

load_dotenv()

from mud_client import MUDClient

from google.adk.agents import LlmAgent

# Define a tool for the ADK LlmAgent to interact with the MUD
def execute_mud_commands(commands: str) -> str:
    """
    Executes a MUD command or a comma-separated list of commands in the MUD server.
    Args:
        commands: A string of MUD commands (e.g. "look" or "south, west, north")
    Returns:
        The command output from the MUD server.
    """
    print(f"\n[ADK Tool] Executing MUD command(s): {commands}")
    client = MUDClient()
    success, login_log = client.login(username="dummy", password="helloworld")
    if not success:
        return f"Failed to log in: {login_log}"
    
    cmd_list = [c.strip() for c in commands.split(",") if c.strip()]
    res = client.execute_commands(cmd_list)
    client.close()
    
    output = ""
    for r in res.get("results", []):
        output += f"=== {r['command']} ===\n{r['output']}\n\n"
    return output

def parse_agent_md() -> dict:
    """Parses agent.md to extract the name, description, and instructions."""
    agent_md_path = "agent.md"
    with open(agent_md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse YAML frontmatter
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

async def main():
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    agent_info = parse_agent_md()
    
    print(f"[+] Initializing Gemini ADK LlmAgent: {agent_info['name']}")
    
    # Instantiate the agent using LlmAgent
    agent = LlmAgent(
        model="gemini-3.5-flash",
        name=agent_info["name"].replace("-", "_"),
        instruction=agent_info["instruction"],
        tools=[execute_mud_commands]
    )
    
    # Set up InMemoryRunner
    runner = InMemoryRunner(agent=agent, app_name="tbamud_player_app")
    
    # Create the session (required by InMemoryRunner)
    user_id = "dummy_user"
    session_id = "tbamud_session"
    await runner.session_service.create_session(
        app_name="tbamud_player_app",
        user_id=user_id,
        session_id=session_id
    )
    
    # Prompt the agent to check the starting room and navigate to the Warrior Guild
    prompt = (
        "You are logged in as 'dummy'. Check your current room, list available exits, "
        "and navigate step-by-step to the Warrior Guild. Based on your instructions, "
        "the guild is located at: Main Street Far East -> South -> East -> South. "
        "Execute the MUD commands necessary to reach the guild and verify arrival."
    )
    
    # Construct types.Content message
    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    
    print(f"[+] Sending prompt to ADK Agent...")
    print("\n--- ADK Agent Response ---")
    
    # Run the agent and process output events
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=msg):
        if getattr(event, "error_message", None):
            print(f"\n[Error] {event.error_message}", file=sys.stderr)
            break
            
        content = getattr(event, "content", None) or getattr(event, "output", None)
        if content and hasattr(content, "parts"):
            for part in content.parts:
                if hasattr(part, "text") and part.text:
                    print(part.text, end="", flush=True)
                    
    print("\n--------------------------")

if __name__ == "__main__":
    asyncio.run(main())
