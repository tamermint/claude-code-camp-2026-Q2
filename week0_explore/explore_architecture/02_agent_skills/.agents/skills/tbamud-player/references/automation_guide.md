# MUD Automation & Agent Strategies

This guide outlines strategies for AI agents playing tbaMUD / CircleMUD.

---

## 1. Output Parsing & Prompt Recognition

CircleMUD prompts typically display vital stats in angle brackets at the bottom of room descriptions:
```text
<100H 100M 100V >
```
- `H` / `hp`: Health Points
- `M` / `m`: Mana Points
- `V` / `mv`: Movement Points

### Handling Telnet & Control Characters
- Strip ANSI control sequences (`\x1b[...]`) before feeding output to LLM prompts.
- Ensure socket reading handles IAC subnegotiations to prevent blocking.

---

## 2. Room Navigation & Mapping

- Parse `Exits: [ n s e w u d ]` from room headers.
- Maintain a local graph (Map) of room IDs, room titles, and directional connections.
- If an exit is closed or locked, issue `open <door>` or `unlock <door>` before moving.

---

## 3. Combat Safety & Healing Loop

1. **Pre-combat Inspection**:
   Always execute `consider <mob>` before engaging unfamiliar targets.
2. **Combat Loop**:
   - Issue `kill <mob>`.
   - Monitor HP in each round prompt.
   - If HP drops below 25%, issue `flee` immediately.
3. **Recovery**:
   - Sit/rest (`rest` or `sleep`) in a safe room to recover HP/Mana.
   - Execute `stand` when fully rested.
