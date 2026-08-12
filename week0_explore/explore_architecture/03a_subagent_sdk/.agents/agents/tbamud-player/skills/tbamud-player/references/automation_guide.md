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

---

## 4. State Persistence & Long-Term Campaign Goals

1. **State Tracking**:
   - Check `data/player_<username>.md` to review character level, stats, active goals, and skill proficiencies.
   - Check `data/world.md` to plan routes to shops, guilds, safe resting spots, and mob spawns.
2. **Campaign Goal Loop (e.g., Reach Level 7 & Defeat Target Boss)**:
   - **Phase 1 (Levels 1-3)**: Fight low-risk mobs (e.g., Fidos, stray dogs), gain EXP, loot gold. Return to shops for weapons/armor and practice skills at the guildmaster.
   - **Phase 2 (Levels 4-6)**: Explore mid-tier zones, practice advanced combat skills/spells, and acquire superior equipment.
   - **Phase 3 (Level 7 & Boss Fight)**: Execute `consider <boss_mob>`, prep healing/buff items, and execute combat loops with strict flee thresholds.
