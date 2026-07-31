import re

# Simple function to parse the room exits
def get_exits(world_file):
    with open(world_file, 'r') as f:
        content = f.read()

    rooms = {}
    room_blocks = re.split(r'#(\d+)', content)
    
    for i in range(1, len(room_blocks), 2):
        vnum = int(room_blocks[i])
        room_data = room_blocks[i+1]
        
        exits = []
        # Find exits (D<dir>...<vnum>)
        # The exit format is D<dir>\n<desc>\n<desc>\n<flags> <key> <to_vnum>
        exit_matches = re.finditer(r'D(\d+)\n.*?\n.*?\n(\d+)\s+(-?\d+)\s+(-?\d+)', room_data, re.DOTALL)
        for match in exit_matches:
            to_vnum = int(match.group(4))
            if to_vnum != -1:
                exits.append(to_vnum)
        rooms[vnum] = exits
        
    return rooms

# Breadth-first search to find shortest path
def find_path(rooms, start, end):
    queue = [(start, [])]
    visited = set()
    
    while queue:
        (node, path) = queue.pop(0)
        if node == end:
            return path + [node]
        if node not in visited:
            visited.add(node)
            for neighbor in rooms.get(node, []):
                queue.append((neighbor, path + [node]))
    return None

rooms = get_exits('/Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week0_explore/circlemud-world-parser/assets/wld/30.wld')
path = find_path(rooms, 3001, 3009)
print(path)
