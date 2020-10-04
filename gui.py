from jinja2 import Environment, FileSystemLoader, select_autoescape
from flask import Flask, render_template, send_from_directory
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

@app.route('/')
def root():
    return env.get_template('gui.html').render(colours=colours)

@app.route('/static/<path:path>')
def static_(path):
    return send_from_directory('static', path)
