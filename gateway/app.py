import collections, json

from session import Session
from flask   import Flask, request

app = Flask(__name__)

@app.route('/connect', methods=['POST'])
def connect():
    data = request.data.decode()
    session = Session(data)
    return session.handle_new_session()

@app.route('/submit', methods=['POST'])
def submit():
    data = request.data.decode()
    session = Session(data)
    return session.handle_submit()

if __name__ == '__main__':
    app.run() # TODO: Add host and port from config
