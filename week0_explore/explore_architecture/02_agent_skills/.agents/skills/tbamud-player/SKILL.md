---
name: tbamud-player
description: >-
  Play, interact with, and automate gameplay in tbaMUD / CircleMUD games running on telnet (e.g., localhost:4000).
  Use this skill when asked to connect to a MUD, issue MUD commands, explore rooms, check player status, or run MUD automation scripts.
---

# tbaMUD / CircleMUD Player Skill

This skill provides tools, command references, and automated procedures for playing and managing sessions on **tbaMUD** (a modern derivative of CircleMUD 3.0/3.1).

---

## Capabilities & Workflows

1. **Session Management & Telnet Connection**:
   - Establish connection to `localhost:4000` (or custom host/port).
   - Manage telnet IAC negotiations and login with player credentials (e.g., `dummy` / `helloworld`).
   - Strip ANSI control sequences for clean AI text processing or retain raw output for display.

2. **Command Execution**:
   - Issue single commands (e.g., `look`, `score`, `inventory`, `north`).
   - Issue batch command sequences.
   - Run interactive telnet sessions.

3. **Autonomous Navigation & Exploration**:
   - Execute room movement (`n`, `s`, `e`, `w`, `u`, `d`).
   - Inspect exits (`exits`), mobs, and room details (`look <object/mob>`).
   - Monitor character stats (`hp`, `mana`, `move`).

---

## Helper Script

The primary helper script for managing telnet connections and command execution is:
[mud_client.py](./scripts/mud_client.py)

### Common Usage Examples

- **Single Command Execution (JSON mode for AI parsing)**:
  ```bash
  python3 .agents/skills/tbamud-player/scripts/mud_client.py --user dummy --password helloworld --cmd "look" --json
  ```

- **Batch Command Execution**:
  ```bash
  python3 .agents/skills/tbamud-player/scripts/mud_client.py --user dummy --password helloworld --cmds "look, score, inventory, exits"
  ```

- **Interactive Session**:
  ```bash
  python3 .agents/skills/tbamud-player/scripts/mud_client.py --user dummy --password helloworld --interactive
  ```

---

## Documentation & References

- [tbaMUD / CircleMUD Command Reference](./references/tbamud_commands.md): Complete list of player and movement commands.
- [AI Automation Guide](./references/automation_guide.md): Strategies for navigation, questing, and combat loops.
- [Programmatic Session Example](./examples/session_example.py): Python example showing custom scripted automation.
