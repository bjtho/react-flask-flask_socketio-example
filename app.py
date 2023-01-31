'''
React/Flask RESTful implementation.
'''

REACT_STATIC_FOLDER = 'react_ui/build'
REACT_TEMPLATE_FOLDER = 'react_ui/build'

import os

# The docs tell you to import this as early as possible. 
# I basically did this at the top of every file for safety.
# Generally speaking all it does is alter the process/thread
# Standard libraries to be friendly with eventlet.
import eventlet
eventlet.monkey_patch()


from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO

react_app = Flask(__name__, static_folder=REACT_STATIC_FOLDER, template_folder=REACT_TEMPLATE_FOLDER)

# Serve whatever restful routes you want.
# I included this just to show how one might serve a built react app.

# @react_app.route('/', defaults={'path': ''})
# @react_app.route('/<path:path>')
# def serve(path):
#     if path != "" and os.path.exists(react_app.static_folder + '/' + path):
#         return send_from_directory(react_app.static_folder, path)
#     else:
#         return send_from_directory(react_app.static_folder, 'index.html')

@react_app.route("/")
def say_hello():
    return jsonify({'data': 'Hello!'})

# init the flask SocketIO server and tell it to use eventlet..    
socketio = SocketIO(react_app, async_mode='eventlet', logger=True, engineio_logger=False, cors_allowed_origins="*")
