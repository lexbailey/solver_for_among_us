from jinja2 import Environment, FileSystemLoader, select_autoescape
from flask import Flask, render_template, send_from_directory, request, Response
from secrets import token_hex
import json
from solve import GameSolver
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=True
)
app = Flask(__name__)

colours = {
    'red': 'c61111'
    ,'blue': '132ed2'
    ,'green': '11802d'
    ,'pink': 'ee54bb'
    ,'orange': 'f07d0d'
    ,'yellow': 'f6f657'
    ,'black': '3f474e'
    ,'white': 'd7e1f1'
    ,'purple': '6b2fbc'
    ,'brown': '71491e'
    ,'cyan': '38ffdd'
    ,'lime': '50f039'
}

running_games = {}

class Game:
    def __init__(self, colours, impostors):
        self.colours = colours
        self.impostors = impostors
        self.solver = GameSolver(len(colours), impostors)
        self.solver.set_colours(colours)

def newgame(colours, impostors):
    token = None
    while token is None or token in running_games:
        token = token_hex(10)
    running_games[token] = Game(colours, impostors)
    return token

@app.route('/')
def root():
    return env.get_template('gui.html').render(colours=colours)

@app.route('/static/<path:path>')
def static_(path):
    return send_from_directory('static', path)

def error(msg):
    return Response(json.dumps({'result':'error', 'msg':msg}), 400, mimetype='application/json')

def success(data):
    return Response(json.dumps({'result':'success', 'msg':'', **data}), 200, mimetype='application/json')

@app.route('/startgame', methods=['POST'])
def start():
    state = request.json
    colours = state.get('colours', [])
    n_players = len(colours)
    n_impostors = state.get('impostors', 0)
    if n_players < 3:
        return error('Too few players, please choose at least three colours.')
    if n_players > 10:
        return error('Too many players, please choose no more than ten players.')
    if n_impostors * 2 >= n_players:
        return error('Too many impostors, game must have more crewmates than imostors.')

    token = newgame(colours, n_impostors)
    return success({'token': token, 'colours': colours, 'msg': 'New game created.'})

@app.route('/learn', methods=['POST'])
def learn():
    d = request.json
    token = d.get('token', '')
    if token not in running_games:
        return error('The game has ended already. Please start a new game to continue.')
    info = d.get('info')
    if info is None:
        return error('No information specified.')
    game = running_games[token]
    print(game, info)
