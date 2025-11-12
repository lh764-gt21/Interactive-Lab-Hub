import time
import paho.mqtt.client as mqtt

players = ["player1", "player2"]
moves = {}   # will store {player_id: move}

def determine_winner(moves_dict):
    """
    Determine the winner from a dictionary of {player: move}
    Returns: (winner_player, result_message)
    """
    if len(moves_dict) < 2:
        return None, "Not enough players"
    
    player1 = players[0]
    player2 = players[1]
    
    if player1 not in moves_dict or player2 not in moves_dict:
        return None, "Missing moves"
    
    move1 = moves_dict[player1]
    move2 = moves_dict[player2]
    
    if move1 == move2:
        return "tie", f"It's a TIE! Both played {move1}"
    
    rules = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }
    
    if rules[move1] == move2:
        return player1, f"{player1} WINS! ({move1} beats {move2})"
    else:
        return player2, f"{player2} WINS! ({move2} beats {move1})"

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Moderator connected!")
    client.subscribe("game/player/+/move")

def on_message(client, userdata, msg):
    global moves
    topic = msg.topic
    payload = msg.payload.decode()
    player = topic.split('/')[2]

    moves[player] = payload
    print(f"[RECV] {player} -> {payload}")

client = mqtt.Client()
client.username_pw_set("idd", "device@theFarm")
client.connect("farlab.infosci.cornell.edu", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_start()

# Game loop
while True:
    moves = {}
    print("\nStarting a new round!")
    client.publish("game/start_round", "rps")

    # wait for all players to respond
    while len(moves) < len(players):
        time.sleep(0.1)

    print("All moves received:", moves)

    # Determine winner
    winner_player, result_message = determine_winner(moves)
    
    print(f"\n{'='*50}")
    print(f"RESULT: {result_message}")
    print(f"{'='*50}\n")
    
    # Publish winner (or "tie" if it's a tie)
    client.publish("game/winner", winner_player if winner_player != "tie" else "tie")

    time.sleep(3)
