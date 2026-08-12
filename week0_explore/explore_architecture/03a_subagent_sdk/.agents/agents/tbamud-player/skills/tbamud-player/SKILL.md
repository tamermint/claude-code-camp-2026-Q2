---
name: tbamud-player
description: >-
  Play, interact with, and automate gameplay in tbaMUD / CircleMUD games running on telnet (e.g., localhost:4000).
  Use this skill when asked to connect to a MUD, issue MUD commands, explore rooms, check player status, or run MUD automation scripts.
---

# tbaMUD / CircleMUD Player Skill

This skill provides tools, command references, state memory tracking, and automated procedures for playing and managing sessions on **tbaMUD** (a modern derivative of CircleMUD 3.0/3.1).

---

## Capabilities & Workflows

1. **Session Management & Telnet Connection**:
   - Establish connection to `localhost:4000` (or custom host/port).
   - Manage telnet IAC negotiations and login with player credentials (e.g., `dummy` / `helloworld`).
   - Strip ANSI control sequences for clean AI text processing or retain raw output for display.

2. **Persistent State Memory & Long-Term Goals**:
   - Maintains character progress in [player_<username>.md](./data/player_<username>.md) (Level, HP/Mana/Move, EXP, Gold, Skills, Goals).
   - Maintains discovered map and vendor data in [world.md](./data/world.md) (Rooms, Exits, Mobs, Guilds, Shops, Danger Zones).
   - Agents MUST inspect and update these memory files when planning multi-step goals (e.g., reaching Level 7, acquiring equipment, defeating boss mobs).

3. **Command Execution**:
   - Issue single commands (e.g., `look`, `score`, `inventory`, `north`, `prac`).
   - Issue batch command sequences.
   - Automatically updates `player_<username>.md` and `world.md` after command runs.

4. **Autonomous Navigation & Exploration**:
   - Execute room movement (`n`, `s`, `e`, `w`, `u`, `d`).
   - Inspect exits (`exits`), mobs, and room details (`look <object/mob>`).
   - Monitor character stats (`hp`, `mana`, `move`).

---

## Players

There are two players in this game.
Our main player: dummy / helloworld
Our secondary player: smarty / goodbyemoon

---

## Helper Scripts & State Files

- **Telnet Client & Automated State Synchronizer**:
  [mud_client.py](./scripts/mud_client.py)
- **State Parsing & Memory Manager**:
  [state_manager.py](./scripts/state_manager.py)
- **Player State Memory**:
  [player_<username>.md](./data/player_<username>.md)
- **World State Memory**:
  [world.md](./data/world.md)

### Common Usage Examples

- **Single Command Execution (JSON mode for AI parsing & State update)**:

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
