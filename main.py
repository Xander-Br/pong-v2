import json
import threading
import time
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

# Game constants
GAME_WIDTH = 800
GAME_HEIGHT = 600
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_SIZE = 10
BALL_SPEED = 5

# Game state
player_positions = {}
player_usernames = {}
ball_x = GAME_WIDTH // 2
ball_y = GAME_HEIGHT // 2
ball_dx = BALL_SPEED
ball_dy = BALL_SPEED

# WebSocket connections
connections = []

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "join":
                username = message["username"]
                player_id = next((player_id for player_id, player_username in player_usernames.items() if player_username == username), None)

                if player_id is not None:
                    # Player already exists, remove the existing player
                    del player_positions[player_id]
                    del player_usernames[player_id]

                player_id = len(player_positions) + 1
                player_positions[player_id] = GAME_HEIGHT // 2 - PADDLE_HEIGHT // 2
                player_usernames[player_id] = username
                await websocket.send_text(json.dumps({"type": "player_id", "player_id": player_id}))
            elif message["type"] == "paddle_move":
                player_id = message["player_id"]
                player_positions[player_id] = message["position"]
            elif message["type"] == "restart":
                # Restart game logic
                global ball_x, ball_y, ball_dx, ball_dy
                ball_x = GAME_WIDTH // 2
                ball_y = GAME_HEIGHT // 2
                ball_dx = BALL_SPEED
                ball_dy = BALL_SPEED
                player_positions.clear()
                player_usernames.clear()
                
                reset_message = json.dumps({"type": "reset"})
                for connection in connections:
                    await connection.send_text(reset_message)
                
                await broadcast_game_state()  

    except:
        connections.remove(websocket)

async def broadcast_game_state():
    while True:
        game_state = {
            "type": "game_state",
            "player_positions": player_positions,
            "player_usernames": player_usernames,
            "ball_position": [ball_x, ball_y],
        }
        for connection in connections:
            await connection.send_text(json.dumps(game_state))
        await asyncio.sleep(0.016)  # 60 FPS

@app.get("/")
async def get():
    # Open the HTML file
    with open("index.html") as file:
        content = file.read()
    return HTMLResponse(content)

def game_loop():
    global ball_x, ball_y, ball_dx, ball_dy

    while True:
        # Update ball position
        ball_x += ball_dx
        ball_y += ball_dy

        # Check for collision with walls
        if ball_y <= 0 or ball_y >= GAME_HEIGHT - BALL_SIZE:
            ball_dy = -ball_dy

        # Check for collision with paddles
        for player_id, player_pos in player_positions.items():
            if (
                ball_x <= PADDLE_WIDTH
                and player_id % 2 == 1
                and player_pos <= ball_y <= player_pos + PADDLE_HEIGHT
            ) or (
                ball_x >= GAME_WIDTH - PADDLE_WIDTH - BALL_SIZE
                and player_id % 2 == 0
                and player_pos <= ball_y <= player_pos + PADDLE_HEIGHT
            ):
                ball_dx = -ball_dx

        # Reset ball if it goes out of bounds
        if ball_x <= 0 or ball_x >= GAME_WIDTH - BALL_SIZE:
            ball_x = GAME_WIDTH // 2
            ball_y = GAME_HEIGHT // 2

        time.sleep(0.016)  # 60 FPS

# Start the game loop in a separate thread
game_thread = threading.Thread(target=game_loop)
game_thread.start()

# Start broadcasting game state
import asyncio
asyncio.create_task(broadcast_game_state())