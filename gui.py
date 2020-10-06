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

def foreach(f):
    def wrap(args):
        for arg in args:
            f(arg)
    return wrap

class Game:
    def __init__(self, colours, impostors):
        self.colours = colours
        self.impostors = impostors
        self.solver = GameSolver(len(colours), impostors)
        self.solver.set_colours(colours)
        
        self.whats = {
            'murdered': foreach(self.solver.learn_murder)
            ,'ejected': foreach(self.solver.learn_ejected)
            ,'crewmate': foreach(self.solver.learn_certain_not_impostor)
            ,'impostor': foreach(self.solver.learn_certain_impostor)
            ,'impostor_in_group': self.solver.learn_set_includes_impostors
        }

    def summary(self):
        summary, n_models = self.solver.check()
        return summary[0:len(self.colours)]

    def learn(self, what, who):
        self.whats[what](who)

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
        return error('Too many impostors, game must have more crewmates than impostors.')

    token = newgame(colours, n_impostors)
    model_summary = running_games[token].summary()
    return success({'token': token, 'impostors': n_impostors, 'colours': colours, 'msg': 'New game created.', 'summary':model_summary})

@app.route('/learn', methods=['POST'])
def learn():
    d = request.json
    token = d.get('token', '')
    if token not in running_games:
        return error('The game has ended already. Please start a new game to continue.')
    what = d.get('what')
    who = d.get('who', [])
    game = running_games[token]
    if what not in game.whats:
        return error('"what" value invalid. No such what "%s".' % what)
    if not who:
        return error('No impostors were specified, please specify at least one impostor')
    for c in who:
        if c not in game.colours:
            return error('Invalid player specified "%s".' % who)
    game.learn(what, who)
    model_summary = running_games[token].summary()
    return success({'token': token, 'impostors': game.impostors, 'colours': game.colours, 'msg': 'Information learned.', 'summary':model_summary})
    print(game)
