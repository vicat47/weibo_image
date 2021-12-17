from utils import DB
from services import *

from flask import Flask, request, render_template, session

import json

app = Flask(__name__)
db = DB('sqlite3', './data/weibo.db')

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('static/home.html')

@app.route('/start', methods=['POST'])
def start_catch():
    request_all_image()

def __init__():
    db.execute_sql('sql/db.sql')

if __name__ == "__main__":
    __init__()
    app.run(host='0.0.0.0', port=5000)