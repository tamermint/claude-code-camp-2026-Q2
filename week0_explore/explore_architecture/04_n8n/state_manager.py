#!/usr/bin/env python3
"""
State Manager for tbaMUD / CircleMUD Player Skill.
Parses MUD command outputs (score, look, exits, list, prac, inventory, equipment)
and updates data/player.md and data/world.md.
"""

import os
import re
import json
from typing import Dict, Any, List

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
WORLD_FILE = os.path.join(DATA_DIR, "world.md")


class StateLock:
    def __init__(self, data_dir: str):
        self.lock_path = os.path.join(data_dir, ".state.lock")
        self.lock_file = None

    def __enter__(self):
        try:
            import fcntl
            self.lock_file = open(self.lock_path, "w")
            fcntl.flock(self.lock_file, fcntl.LOCK_EX)
        except (ImportError, OSError):
            pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_file:
            try:
                import fcntl
                fcntl.flock(self.lock_file, fcntl.LOCK_UN)
            except (ImportError, OSError):
                pass
            try:
                self.lock_file.close()
            except Exception:
                pass


def get_player_file(username: str = None) -> str:
    """Get path to the player state markdown file."""
    if not username:
        username = "dummy"
    return os.path.join(DATA_DIR, f"player_{username.lower()}.md")


def get_default_player_section(username: str = None) -> str:
    """Extract only the default section for the given username from DEFAULT_PLAYER_MD."""
    if not username:
        return DEFAULT_PLAYER_MD
    
    sections = DEFAULT_PLAYER_MD.split("\n## ")
    header = sections[0]
    for sec in sections[1:]:
        lines = sec.splitlines()
        if not lines:
            continue
        first_line = lines[0].strip()
        name_match = re.match(r"^(\w+)", first_line)
        if name_match and name_match.group(1).lower() == username.lower():
            return header.rstrip() + "\n\n## " + sec.strip() + "\n"
    return DEFAULT_PLAYER_MD


def ensure_data_files(username: str = None):
    """Ensure data directory and state markdown files exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    player_file = get_player_file(username)
    if not os.path.exists(player_file):
        with open(player_file, "w", encoding="utf-8") as f:
            f.write(get_default_player_section(username))
    if not os.path.exists(WORLD_FILE):
        with open(WORLD_FILE, "w", encoding="utf-8") as f:
            f.write(DEFAULT_WORLD_MD)


DEFAULT_PLAYER_MD = """# Player State Memory

## Dummy (Warrior)
### Character Info
- **Name**: Dummy
- **Class**: Warrior
- **Title**: Dummy the Swordpupil
- **Level**: 1
- **Age**: 17
- **Target Goal**: Reach Level 7 & Defeat Target Boss Monster

### Stats & Vitals
- **HP**: 22 / 22
- **Mana**: 100 / 100
- **Move**: 71 / 85
- **Armor Class**: 100/10
- **Alignment**: 0

### Progression
- **Current EXP**: 1
- **EXP Needed for Next Level**: 1999
- **Gold**: 0 coins
- **Quest Points**: 0

### Skills & Spells
- `kick`: bad (0 sessions remaining)

### Equipment & Inventory
- **Equipment**: None equipped
- **Inventory**: Empty

### Active Goals
- [ ] Explore Midgaard and train basic skills
- [ ] Acquire weapons and armor
- [ ] Level up to Level 7
- [ ] Locate and defeat target boss monster

## Smarty (Mage)
### Character Info
- **Name**: Smarty
- **Class**: Mage
- **Title**: Smarty the Apprentice of Magic
- **Level**: 1
- **Age**: 17
- **Target Goal**: Reach Level 7 & Defeat Target Boss Monster

### Stats & Vitals
- **HP**: 14 / 14
- **Mana**: 100 / 100
- **Move**: 83 / 83
- **Armor Class**: 90/10
- **Alignment**: 0

### Progression
- **Current EXP**: 1
- **EXP Needed for Next Level**: 2499
- **Gold**: 0 coins
- **Quest Points**: 0

### Skills & Spells
- `kick`: bad (0 sessions remaining)

### Equipment & Inventory
- **Equipment**: None equipped
- **Inventory**: Empty

### Active Goals
- [ ] Explore Midgaard and train basic skills
- [ ] Acquire weapons and armor
- [ ] Level up to Level 7
- [ ] Locate and defeat target boss monster
"""

DEFAULT_WORLD_MD = """# World State Memory (Midgaard & Surrounding Realms)

## Key Locations & Discovered Rooms

| Room Name | Exits | Notable Mobs / Features |
|---|---|---|
| The Temple Of Midgaard | N, E, S, W, D | ATM, Temple Gate |
| The Temple Square | N, E, S, W | Marble Fountain |
| Market Square | N, E, S, W | Peacekeeper, Statue, Cityguard |
| Main Street (West) | N, E, S, W | Bakery (N), Armory (S) |
| The Bakery | S | Baker (Danish 7c, Bread 14c, Waybread 72c) |
| Main Street (Far West) | N, E, S, W | Magic Shop (N), Mages' Guild (S), West Gate (W), Fido |
| Main Street (East) | N, E, S, W | General Store (N), Pet Shop (S) |
| Main Street (Far East) | N, E, S, W | Weapon Shop (N), Guild of Swordsmen (S), East Gate (E), Fido |
| Entrance to Guild of Swordsmen | N, E | Knight Guard, Peacekeeper, ATM |
| Bar of Swordsmen | S, W | Waiter, Bulletin Board |
| Tournament and Practice Yard | N, D | **Guildmaster**, Well leading down |

## Shops & Vendors
- **Bakery**: Danish Pastry (7c), Bread (14c), Waybread (72c)
- **Armory**: Main Street West -> South
- **Weapon Shop**: Main Street Far East -> North
- **General Store**: Main Street East -> North
- **Magic Shop**: Main Street Far West -> North

## Guilds
- **Warrior (Swordsmen)**: Main Street Far East -> South -> East -> South (Guildmaster in Practice Yard)
- **Mage**: Main Street Far West -> South
- **Cleric**: Temple Square -> West

## Danger Zones & Monsters
- **Fidos / Scavengers**: Main Street (Low level / Neutral)
- **Dark Well**: Down from Warrior Practice Yard (Unexplored)
"""


def parse_and_update_state(command_results: List[Dict[str, str]], username: str = None):
    """Parse outputs from MUD command results and update player.md & world.md."""
    with StateLock(DATA_DIR):
        ensure_data_files(username)
        
        score_data = {}
        room_data = {}

        for res in command_results:
            cmd = res.get("command", "").strip().lower()
            out = res.get("output", "")

            # Parse score
            if cmd == "score" or "ranks you as" in out.lower():
                m_age = re.search(r"You are (\d+) years old", out)
                m_stats = re.search(r"(\d+)\((\d+)\)\s+hit,\s+(\d+)\((\d+)\)\s+mana\s+and\s+(\d+)\((\d+)\)\s+movement", out)
                m_ac = re.search(r"armor class is ([^,]+)", out)
                m_align = re.search(r"alignment is ([-\d]+)", out)
                m_exp = re.search(r"have (\d+) exp,\s+(\d+) gold coins", out)
                m_need = re.search(r"need (\d+) exp to reach your next level", out)
                m_rank = re.search(r"ranks you as (.*?)\s+\(level (\d+)\)", out)

                if m_rank:
                    title = m_rank.group(1)
                    score_data["title"] = title
                    score_data["level"] = m_rank.group(2)
                    name_match = re.match(r"^(\w+)", title)
                    if name_match:
                        score_data["name"] = name_match.group(1)
                    if "Apprentice of Magic" in title:
                        score_data["class"] = "Mage"
                    elif "Swordpupil" in title:
                        score_data["class"] = "Warrior"
                    else:
                        score_data["class"] = "Unknown"
                if m_stats:
                    score_data["hp"] = f"{m_stats.group(1)} / {m_stats.group(2)}"
                    score_data["mana"] = f"{m_stats.group(3)} / {m_stats.group(4)}"
                    score_data["move"] = f"{m_stats.group(5)} / {m_stats.group(6)}"
                if m_ac:
                    score_data["ac"] = m_ac.group(1)
                if m_align:
                    score_data["alignment"] = m_align.group(1)
                if m_exp:
                    score_data["exp"] = m_exp.group(1)
                    score_data["gold"] = m_exp.group(2)
                if m_need:
                    score_data["exp_needed"] = m_need.group(1)
                if m_age:
                    score_data["age"] = m_age.group(1)

            elif cmd == "equipment" or "you are using:" in out.lower():
                lines = [l.strip() for l in out.splitlines() if l.strip()]
                eq_items = []
                for line in lines:
                    if line.lower().startswith("you are using:") or "H " in line and "V " in line:
                        continue
                    if line.strip().lower() == "nothing.":
                        continue
                    m_eq = re.match(r"<[^>]+>\s+(.*)", line)
                    if m_eq:
                        eq_items.append(m_eq.group(1).strip())
                
                if eq_items:
                    from collections import Counter
                    counts = Counter(eq_items)
                    eq_strs = []
                    for item, count in counts.items():
                        if count > 1:
                            eq_strs.append(f"{count}x {item}")
                        else:
                            eq_strs.append(item)
                    score_data["equipment"] = ", ".join(eq_strs)
                else:
                    score_data["equipment"] = "None equipped"

            elif cmd == "inventory" or "you are carrying:" in out.lower():
                lines = [l.strip() for l in out.splitlines() if l.strip()]
                inv_items = []
                for line in lines:
                    if line.lower().startswith("you are carrying:") or "H " in line and "V " in line:
                        continue
                    if line.strip().lower() == "nothing.":
                        continue
                    inv_items.append(line.strip())
                
                if inv_items:
                    from collections import Counter
                    counts = Counter(inv_items)
                    inv_strs = []
                    for item, count in counts.items():
                        if count > 1:
                            inv_strs.append(f"{count}x {item}")
                        else:
                            inv_strs.append(item)
                    score_data["inventory"] = ", ".join(inv_strs)
                else:
                    score_data["inventory"] = "Empty"

            # Parse look / room
            elif cmd in ("look", "l") or "[ Exits:" in out:
                lines = [l.strip() for l in out.splitlines() if l.strip()]
                if lines and "[ Exits:" in out:
                    room_title = lines[0]
                    exits_match = re.search(r"\[ Exits:\s*([^\]]+)\s*\]", out)
                    exits_str = exits_match.group(1).upper() if exits_match else "None"
                    mobs_and_objs = []
                    for line in lines[1:]:
                        if line.startswith("[ Exits:") or "H " in line and "V " in line:
                            continue
                        if any(kw in line.lower() for kw in ["is here", "standing here", "guarding", "wiping flour", "mucking"]):
                            mobs_and_objs.append(line)
                    room_data[room_title] = {
                        "exits": exits_str,
                        "features": "; ".join(mobs_and_objs) if mobs_and_objs else "Clear"
                    }

        if score_data:
            update_player_md(score_data, username)
        if room_data:
            update_world_md(room_data)


def update_player_md(data: Dict[str, str], username: str = None):
    """Update stats for a specific player section inside player_<username>.md."""
    player_name = data.get("name", "Dummy").capitalize()
    player_file = get_player_file(username)
    
    # Read current content or start with default
    content = ""
    if os.path.exists(player_file):
        with open(player_file, "r", encoding="utf-8") as f:
            content = f.read()
            
    if not content.strip():
        content = get_default_player_section(username)

    # Split content into sections by '## '
    sections = content.split("\n## ")
    header = sections[0]
    player_sections = {}
    
    for sec in sections[1:]:
        lines = sec.splitlines()
        if not lines:
            continue
        first_line = lines[0].strip()
        name_match = re.match(r"^(\w+)", first_line)
        if name_match:
            sec_name = name_match.group(1).capitalize()
            player_sections[sec_name] = "\n".join(lines[1:])
            
    # Default template for a new player section
    default_section_template = """### Character Info
- **Name**: {name}
- **Class**: {class_name}
- **Title**: {title}
- **Level**: {level}
- **Age**: {age}
- **Target Goal**: Reach Level 7 & Defeat Massive Minotaur (Newbie Zone North of Midgaard)

### Stats & Vitals
- **HP**: {hp}
- **Mana**: {mana}
- **Move**: {move}
- **Armor Class**: {ac}
- **Alignment**: {alignment}

### Progression
- **Current EXP**: {exp}
- **EXP Needed for Next Level**: {exp_needed}
- **Gold**: {gold} coins
- **Quest Points**: {quest_points}

### Skills & Spells
- `kick`: bad (0 sessions remaining)

### Equipment & Inventory
- **Equipment**: {equipment}
- **Inventory**: {inventory}

### Active Goals
- [x] Explore Newbie Zone north of Midgaard and locate Minotaur Lair
- [ ] Grinding Phase (Levels 1-3): Slay Creepy Crawlers to earn EXP and Gold
- [ ] Gear Up Phase: Buy armor from Armory & weapon from Weapon Shop
- [ ] Training Phase: Train kick and physical skills at Warrior Guildmaster
- [ ] Reaching Level 7: Level up character to level 7
- [ ] Boss Raid: Enter Alchemist's Room stairs down (`d`), `consider minotaur`, and defeat the Massive Minotaur!
"""

    player_class = data.get("class", "Warrior" if player_name == "Dummy" else "Mage")
    title = data.get("title", f"{player_name} the Apprentice")
    level = data.get("level", "1")
    age = data.get("age", "17")
    hp = data.get("hp", "10 / 10")
    mana = data.get("mana", "100 / 100")
    move = data.get("move", "80 / 80")
    ac = data.get("ac", "100/10")
    alignment = data.get("alignment", "0")
    exp = data.get("exp", "0")
    exp_needed = data.get("exp_needed", "2000")
    gold = data.get("gold", "0")
    quest_points = data.get("quest_points", "0")
    equipment = data.get("equipment", "None equipped")
    inventory = data.get("inventory", "Empty")

    sec_content = player_sections.get(player_name)
    if not sec_content:
        sec_content = default_section_template.format(
            name=player_name,
            class_name=player_class,
            title=title,
            level=level,
            age=age,
            hp=hp,
            mana=mana,
            move=move,
            ac=ac,
            alignment=alignment,
            exp=exp,
            exp_needed=exp_needed,
            gold=gold,
            quest_points=quest_points,
            equipment=equipment,
            inventory=inventory
        )
    else:
        # Update existing fields
        if "name" in data:
            sec_content = re.sub(r"- \*\*Name\*\*: .*", f"- **Name**: {data['name']}", sec_content)
        if "class" in data:
            sec_content = re.sub(r"- \*\*Class\*\*: .*", f"- **Class**: {data['class']}", sec_content)
        if "title" in data:
            sec_content = re.sub(r"- \*\*Title\*\*: .*", f"- **Title**: {data['title']}", sec_content)
        if "level" in data:
            sec_content = re.sub(r"- \*\*Level\*\*: .*", f"- **Level**: {data['level']}", sec_content)
        if "age" in data:
            sec_content = re.sub(r"- \*\*Age\*\*: .*", f"- **Age**: {data['age']}", sec_content)
        if "hp" in data:
            sec_content = re.sub(r"- \*\*HP\*\*: .*", f"- **HP**: {data['hp']}", sec_content)
        if "mana" in data:
            sec_content = re.sub(r"- \*\*Mana\*\*: .*", f"- **Mana**: {data['mana']}", sec_content)
        if "move" in data:
            sec_content = re.sub(r"- \*\*Move\*\*: .*", f"- **Move**: {data['move']}", sec_content)
        if "ac" in data:
            sec_content = re.sub(r"- \*\*Armor Class\*\*: .*", f"- **Armor Class**: {data['ac']}", sec_content)
        if "alignment" in data:
            sec_content = re.sub(r"- \*\*Alignment\*\*: .*", f"- **Alignment**: {data['alignment']}", sec_content)
        if "exp" in data:
            sec_content = re.sub(r"- \*\*Current EXP\*\*: .*", f"- **Current EXP**: {data['exp']}", sec_content)
        if "gold" in data:
            sec_content = re.sub(r"- \*\*Gold\*\*: .*", f"- **Gold**: {data['gold']} coins", sec_content)
        if "exp_needed" in data:
            sec_content = re.sub(r"- \*\*EXP Needed for Next Level\*\*: .*", f"- **EXP Needed for Next Level**: {data['exp_needed']}", sec_content)
        if "equipment" in data:
            sec_content = re.sub(r"- \*\*Equipment\*\*: .*", f"- **Equipment**: {data['equipment']}", sec_content)
        if "inventory" in data:
            sec_content = re.sub(r"- \*\*Inventory\*\*: .*", f"- **Inventory**: {data['inventory']}", sec_content)

    player_sections[player_name] = sec_content

    # Reconstruct player file
    new_content = header.rstrip() + "\n"
    for name in sorted(player_sections.keys()):
        if username and name.lower() != username.lower():
            continue
        p_class = data.get("class", "Warrior" if name == "Dummy" else "Mage")
        m_class = re.search(r"- \*\*Class\*\*: (.*)", player_sections[name])
        sec_class = m_class.group(1).strip() if m_class else p_class
        new_content += f"\n## {name} ({sec_class})\n{player_sections[name].strip()}\n"

    with open(player_file, "w", encoding="utf-8") as f:
        f.write(new_content)


def update_world_md(room_data: Dict[str, Dict[str, str]]):
    """Add or update rooms in data/world.md key locations table."""
    if not os.path.exists(WORLD_FILE):
        return

    with open(WORLD_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    for room_name, info in room_data.items():
        # Escape pipe characters in room_name or features
        clean_name = room_name.replace("|", "-")
        clean_exits = info["exits"].replace("|", "-")
        clean_feat = info["features"].replace("|", "-")

        if clean_name in content:
            continue  # Already in world.md table
        
        # Append new row before ## Shops & Vendors or at end of table
        new_row = f"| {clean_name} | {clean_exits} | {clean_feat} |\n"
        if "## Shops & Vendors" in content:
            content = content.replace("## Shops & Vendors", f"{new_row}\n## Shops & Vendors")
        else:
            content += f"\n{new_row}"

    with open(WORLD_FILE, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    with StateLock(DATA_DIR):
        ensure_data_files()
    print(f"[INFO] State files verified at {DATA_DIR}")
