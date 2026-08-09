# tbaMUD / CircleMUD Command Quick Reference

This document details common commands available in tbaMUD (CircleMUD derivative).

---

## 1. Navigation & Movement
- `north` (`n`): Move north
- `south` (`s`): Move south
- `east` (`e`): Move east
- `west` (`w`): Move west
- `up` (`u`): Move up
- `down` (`d`): Move down
- `exits`: List all available obvious exits in the current room
- `look` (`l`): Inspect current room or specified item/character (e.g. `look sign`, `look guard`)
- `scan`: Briefly scan adjacent rooms for occupants

---

## 2. Character & Inventory
- `score` (`sc`): View level, HP, Mana, Movement, Gold, Experience, and Alignments
- `inventory` (`i`): List items currently carried in your inventory
- `equipment` (`eq`): List items currently worn/equipped
- `attribute` / `affects`: Check active spells, buffs, or debuffs
- `wear <item>`: Equip an item from inventory
- `remove <item>`: Unequip an item and return it to inventory
- `get <item>` / `get all`: Pick up items from the room ground or container
- `drop <item>` / `drop all`: Drop items onto the room floor

---

## 3. Combat Commands
- `kill <mob>` (`k <mob>`): Initiate combat against a monster/mob
- `flee`: Attempt to escape from active combat into an adjacent room
- `consider <mob>` (`con <mob>`): Compare your level/strength against a target before fighting
- `assist <player>`: Join combat helping another player or friendly mob
- `cast '<spell>' <target>`: Cast a spell (e.g., `cast 'magic missile' fido`)

---

## 4. Communication & Social
- `say <message>`: Speak to everyone in the current room
- `gossip <message>`: Broadcast a message across the global MUD gossip channel
- `tell <character> <message>`: Send a private message to a specific online character
- `who`: View a list of online players, levels, and titles
- `help <topic>`: Access built-in MUD documentation for commands or spells

---

## 5. Utility Commands
- `prompt`: Customize or view your status prompt format (e.g., `<%h/hp %m/m %v/mv>`)
- `save`: Save character status and inventory immediately
- `quit`: Log out of the MUD safely
