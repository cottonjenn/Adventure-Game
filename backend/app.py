from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initial game state
def init_game():
    return {
        'location': 'clearing',
        'inventory': [],
        'health': 100
    }

# Global player state
player = init_game()

rooms = {
    'clearing': {
        'desc': 'You are in a forest clearing. Paths lead north and east.',
        'north': 'cave',
        'east': 'river',
        'items': ['map', 'apple', 'torch']
    },
    'cave': {
        'desc': 'A dark cave with strange noises. You feel uneasy.',
        'south': 'clearing',
        'items': ['torch', 'old coin', 'silver key', 'sword'],
        'enemy': 'giant spider',
        'enemy_health': 30
    },
    'river': {
        'desc': 'A flowing river blocks your way. There’s a bridge to the north.',
        'west': 'clearing',
        'north': 'tower',
        'locked': {'north': 'silver key'},
        'items': ['fishing rod', 'shield']
    },
    'tower': {
        'desc': 'You enter a tall, ancient tower. A chill runs down your spine...',
        'south': 'river',
        'items': ['ancient book'],
        'enemy': 'shadow beast',
        'enemy_health': 50
    }
}

def show_location():
    loc = player['location']
    room = rooms[loc]
    output = room['desc']

    if room.get('items'):
        output += "\nOn the ground, you see:"
        for item in room['items']:
            output += f"\n  - {item}"

    if 'enemy' in room:
        output += f"\n⚔️ A {room['enemy']} lurks here with {room['enemy_health']} health remaining."

    if loc == 'tower' and 'ancient book' in player['inventory']:
        output += "\n📖 You open the ancient book inside the tower.\n✨ Light bursts from the pages, and the shadow beast vanishes!\n🎉 You have completed your quest and won the game!"
        if 'enemy' in room:
            del room['enemy']
            del room['enemy_health']
        return output, True, room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])

    return output, False, room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])

def move(direction):
    loc = player['location']
    room = rooms[loc]

    if direction in room.get('locked', {}):
        required_item = room['locked'][direction]
        if required_item not in player['inventory']:
            return f"The path {direction} is locked. You need the {required_item}.", False, None, None, None, None, room.get('items', [])
    
    if direction in room:
        player['location'] = room[direction]
        return show_location()
    return f"You can't go {direction} from here.", False, room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])

# Update other functions to return directions and items
def fight():
    loc = player['location']
    room = rooms[loc]
    if 'enemy' not in room:
        return "There’s nothing to fight here.", False, room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])
    # ... (rest of fight logic unchanged)
    return output, game_over, room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])

def take_item(item):
    loc = player['location']
    room = rooms[loc]
    if item in room.get('items', []):
        player['inventory'].append(item)
        room['items'].remove(item)
        return f"You picked up the {item}.", False, room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])
    return f"There is no {item} here.", False, room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])

def drop_item(item):
    loc = player['location']
    room = rooms[loc]
    if item in player['inventory']:
        player['inventory'].remove(item)
        room['items'].append(item)
        return f"You dropped the {item}.", False, room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])
    return f"You don’t have {item}.", False, room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])

def use_item(item):
    loc = player['location']
    room = rooms[loc]
    # ... (rest of use_item logic unchanged)
    return output, False, room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])

@app.route('/start', methods=['GET'])
def start_game():
    output, game_over, north, south, east, west, items = show_location()
    return jsonify({
        'room_description': output,
        'inventory': player['inventory'],
        'health': player['health'],
        'game_over': game_over,
        'directions': {'north': north, 'south': south, 'east': east, 'west': west},
        'items': items
    })

@app.route('/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    command = data.get('command', '').lower().strip()
    loc = player['location']
    room = rooms[loc]

    if command == 'look':
        output, game_over, north, south, east, west, items = show_location()
    elif command.startswith('go '):
        direction = command.split(' ', 1)[1]
        output, game_over, north, south, east, west, items = move(direction)
    elif command.startswith('take '):
        item = command.split(' ', 1)[1]
        output, game_over, north, south, east, west, items = take_item(item)
    elif command.startswith('drop '):
        item = command.split(' ', 1)[1]
        output, game_over, north, south, east, west, items = drop_item(item)
    elif command.startswith('use '):
        item = command.split(' ', 1)[1]
        output, game_over, north, south, east, west, items = use_item(item)
    elif command == 'fight':
        output, game_over, north, south, east, west, items = fight()
    elif command == 'inventory':
        output = "You are carrying:\n" + "\n".join(f"- {item}" for item in player['inventory']) if player['inventory'] else "Your inventory is empty."
        game_over = False
        north, south, east, west, items = room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])
    elif command == 'quit':
        output, game_over = "Thanks for playing!", True
        north, south, east, west, items = None, None, None, None, room.get('items', [])
    else:
        output, game_over = "Unknown command. Try 'go north', 'take torch', 'use apple', 'fight', 'inventory', or 'quit'.", False
        north, south, east, west, items = room.get('north'), room.get('south'), room.get('east'), room.get('west'), room.get('items', [])

    return jsonify({
        'room_description': output,
        'inventory': player['inventory'],
        'health': player['health'],
        'game_over': game_over,
        'directions': {'north': north, 'south': south, 'east': east, 'west': west},
        'items': items
    })

@app.route('/reset', methods=['GET'])
def reset_game():
    global player
    player = init_game()
    for room in rooms.values():
        if room['desc'] == rooms['clearing']['desc']:
            room['items'] = ['map', 'apple', 'torch']
        elif room['desc'] == rooms['cave']['desc']:
            room['items'] = ['torch', 'old coin', 'silver key', 'sword']
            room['enemy'] = 'giant spider'
            room['enemy_health'] = 30
        elif room['desc'] == rooms['river']['desc']:
            room['items'] = ['fishing rod', 'shield']
        elif room['desc'] == rooms['tower']['desc']:
            room['items'] = ['ancient book']
            room['enemy'] = 'shadow beast'
            room['enemy_health'] = 50
    output, game_over, north, south, east, west, items = show_location()
    return jsonify({
        'room_description': output,
        'inventory': player['inventory'],
        'health': player['health'],
        'game_over': game_over,
        'directions': {'north': north, 'south': south, 'east': east, 'west': west},
        'items': items
    })

# ... (rest of your code unchanged)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
