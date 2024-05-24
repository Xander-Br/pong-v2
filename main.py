from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, send, emit
from uuid import uuid4
from threading import Thread, Event
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

players = {}
teams = {
    'team1': [],
    'team2': []
}

bot_count = 0

class Player:
    def __init__(self, sid, is_bot=False):
        self.sid = sid
        self.id = str(uuid4())  # unique player ID
        self.name = None
        self.team = None
        self.paddle_y = 50
        self.is_bot = is_bot
        self.thread = None

class Team:
    def __init__(self, name):
        self.name = name
        self.score = 0

team1 = Team('Team 1')
team2 = Team('Team 2')

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 50
        self.y = 50
        self.vx = 2 * (-1 if uuid4().int % 2 == 0 else 1)*0.5
        self.vy = 2 * (-1 if uuid4().int % 2 == 0 else 1)*0.5

    def move(self):
        self.x += self.vx
        self.y += self.vy
        if self.y <= 0 or self.y >= 100:
            self.vy = -self.vy

ball = Ball()

class Game:
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2
        self.state = 'idle'  # states: 'idle', 'playing'
        self.thread = None
        self.stop_event = Event()

    def start_game(self):
        if self.state == 'idle':
            self.state = 'playing'
            self.stop_event.clear()
            self.thread = Thread(target=self.run)
            self.thread.start()
            self.broadcast_state()

    def run(self):
        while not self.stop_event.is_set():
            start_time = time.time()
            # Game logic
            ball.move()
            self.check_collisions()
            self.broadcast_tick()
            elapsed_time = time.time() - start_time
            time.sleep(max(1/60 - elapsed_time, 0))  # simulate 60 fps
        self.state = 'idle'
        self.broadcast_state()

    def stop_game(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        for player in players.values():
            if player.is_bot and player.thread:
                player.thread.join()
        self.state = 'idle'
        self.broadcast_state()

    def check_collisions(self):
        # Check for paddle collisions
        for player in players.values():
            self.check_paddle_collision(player)
        # Check for scoring
        if ball.x <= 0:
            self.team2.score += 1
            ball.reset()
            self.broadcast_state()
        if ball.x >= 100:
            self.team1.score += 1
            ball.reset()
            self.broadcast_state()

    def check_paddle_collision(self, player):
        paddle_top = player.paddle_y - 10
        paddle_bottom = player.paddle_y + 10
        if player.team == 'Team 1' and ball.x <= 2 and paddle_top <= ball.y <= paddle_bottom:
            ball.vx = -ball.vx
        if player.team == 'Team 2' and ball.x >= 98 and paddle_top <= ball.y <= paddle_bottom:
            ball.vx = -ball.vx

    def broadcast_state(self):
        socketio.emit('game_state', {
            'state': self.state,
            'teams': self.get_team_data(),
            'score': {'team1': self.team1.score, 'team2': self.team2.score},
            'players': {player.id: {'team': player.team, 'paddle_y': player.paddle_y, 'is_bot': player.is_bot} for player in players.values()}
        }, to=None)

    def broadcast_tick(self):
        with app.app_context():
            socketio.emit('game_tick', {
                'ball': {'x': ball.x, 'y': ball.y},
                'paddles': {player.id: {'paddle_y': player.paddle_y, 'team': player.team, 'is_bot': player.is_bot} for player in players.values()}
            }, to=None)

    def get_team_data(self):
        return {
            'team1': [{'id': player.id, 'name': player.name} for player in teams['team1']],
            'team2': [{'id': player.id, 'name': player.name} for player in teams['team2']]
        }

game = Game(team1, team2)

@app.route("/")
def index():
    return send_from_directory('', 'index.html')

@socketio.on('connect')
def handle_connect():
    player = Player(request.sid)
    if len(teams['team1']) <= len(teams['team2']):
        player.team = 'Team 1'
        teams['team1'].append(player)
    else:
        player.team = 'Team 2'
        teams['team2'].append(player)
    players[request.sid] = player
    print(f'Player connected: {player.id} assigned to {player.team}')
    emit('player_id', {'player_id': player.id, 'team': player.team}, room=request.sid)

@socketio.on('set_username')
def handle_set_username(username):
    player = players.get(request.sid)
    if player:
        player.name = username
        print(f'Player {player.id} set their username to {username}')
        game.broadcast_state()
        

@socketio.on('disconnect')
def handle_disconnect():
    player = players.pop(request.sid, None)
    if player:
        teams[player.team.lower().replace(' ', '')].remove(player)
        print(f'Player disconnected: {player.id} from {player.team}')
        # Stop the game if a player disconnects
        if game.state == 'playing':
            game.stop_game()
        game.broadcast_state()

@socketio.on('message')
def handle_message(msg):
    player = players.get(request.sid)
    if player:
        print(f'Received message from {player.id} ({player.team}): {msg}')
        # Check if the message is a command to start the game
        if msg == "!start" and player.name == "Xander":
            game.start_game()
        elif msg.startswith("!addBot") and player.name == "Xander":
            add_bot()
        elif msg.startswith("!removeBot") and player.name == "Xander":
            if msg.strip() == "!removeBot all":
                remove_all_bots()
            else:
                remove_bot()
        else:
            send(f'{player.team} ({player.name}): {msg}', broadcast=True)

@socketio.on('paddle_move')
def handle_paddle_move(data):
    player = players.get(request.sid)
    if player:
        new_y = player.paddle_y + data['paddle_y']
        player.paddle_y = max(0, min(100, new_y))


def add_bot():
    global bot_count
    bot_count += 1
    bot_sid = str(uuid4())
    bot = Player(bot_sid, is_bot=True)
    bot.name = f'Bot {bot_count}'
    if len(teams['team1']) <= len(teams['team2']):
        bot.team = 'Team 1'
        teams['team1'].append(bot)
    else:
        bot.team = 'Team 2'
        teams['team2'].append(bot)
    players[bot_sid] = bot
    print(f'Bot added to {bot.team} with name {bot.name}')
    bot.thread = Thread(target=run_bot, args=(bot,))
    bot.thread.start()
    game.broadcast_state()

def remove_bot():
    global bot_count
    bot_sids = [sid for sid, player in players.items() if player.is_bot]
    if bot_sids:
        bot_sid = bot_sids[-1]
        bot = players.pop(bot_sid)
        teams[bot.team.lower().replace(' ', '')].remove(bot)
        print(f'Bot removed from {bot.team} with name {bot.name}')
        bot.thread.join()
        bot_count -= 1
        game.broadcast_state()

def remove_all_bots():
    global bot_count
    bot_sids = [sid for sid, player in players.items() if player.is_bot]
    for bot_sid in bot_sids:
        bot = players.pop(bot_sid)
        teams[bot.team.lower().replace(' ', '')].remove(bot)
        print(f'Bot removed from {bot.team} with name {bot.name}')
        bot.thread.join()
    bot_count = 0
    game.broadcast_state()

def run_bot(bot):
    while not game.stop_event.is_set():
        if bot.team == 'Team 1' and ball.x < 50 or bot.team == 'Team 2' and ball.x > 50:
            if ball.y > bot.paddle_y + 5:
                bot.paddle_y = min(100, bot.paddle_y + 2)
            elif ball.y < bot.paddle_y - 5:
                bot.paddle_y = max(0, bot.paddle_y - 2)
        time.sleep(1/30)  # bot reaction time

if __name__ == '__main__':
    socketio.run(app, debug=True)