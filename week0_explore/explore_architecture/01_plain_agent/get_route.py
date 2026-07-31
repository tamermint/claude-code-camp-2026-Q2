import json

def get_route(wld_json_path, start_vnum, end_vnum):
    with open(wld_json_path, 'r') as f:
        rooms_list = json.load(f)
        
    rooms = {room['id']: room for room in rooms_list}
    
    # BFS to find shortest path
    queue = [(start_vnum, [])]
    visited = set()
    
    direction_map = {
        0: 'north',
        1: 'east',
        2: 'south',
        3: 'west',
        4: 'up',
        5: 'down'
    }
    
    while queue:
        node, path = queue.pop(0)
        if node == end_vnum:
            return path
        if node not in visited:
            visited.add(node)
            room = rooms.get(node)
            if room:
                for ext in room.get('exits', []):
                    to_vnum = ext['room_linked']
                    direction_code = ext['dir']
                    direction_name = direction_map.get(direction_code, str(direction_code))
                    queue.append((to_vnum, path + [(node, direction_name, to_vnum)]))
    return None

wld_path = '/Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week0_explore/preview/data/world/wld/30.json'
route = get_route(wld_path, 3001, 3009)
if route:
    print("Found route:")
    for step in route:
        print(f"From room {step[0]} go {step[1]} to {step[2]}")
else:
    print("Route not found.")
