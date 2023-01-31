'''
SocketIO Implementation + entrypoint.
'''

PORT = 9999 # Both flask, and socketio will listen on this port.
TIMEOUT = 5 # Timeout for the subprocess function.

# hello again monkey
import eventlet
eventlet.monkey_patch()

from app import socketio, react_app

# do your server route stuff here.
@socketio.on('connect')
def handle_connect(*args):
    # do connection things
    print(f"Client is connected.")


@socketio.on('disconnect')
def handle_disconnect(*args):
    # do disconnection things.
    print("Client is disconnected.")

emit_process_spawned = False

# This function emits a counter value every n seconds.
# It is spawned in an eventlet subprocess for concurrency.
# It uses the already initialized socketio object. 
def emit_event_periodically(n):
    global emit_process_spawned
    # We need this for eventlet/gunicorn because it will try to launch new threads 
    # Every time it decides to launch a new worker.
    if emit_process_spawned:
        return
    
    emit_process_spawned = True
    
    counter = 0
    
    while True:
        # do stuff.
        socketio.emit('my_topic', {'counter': counter})
        counter+=1
        socketio.sleep(n)

# Normal, windows 10 compatable runtime. This is what I use for development because it's a PITA
# to constantly build to Docker for every little change.
def start_server():
    eventlet.spawn(emit_event_periodically, TIMEOUT)
     # emit event every 10 seconds
    print(f"Starting server on {PORT}"),
    socketio.run(react_app, port=PORT, debug=False)
    return


# if you have to use Gunicorn you can call this function instead of server.py. Something like:
# gunicorn -k "eventlet" -b "0.0.0.0:8000" --threads 100 server:gunicorn_app()
# long and short, gunicorn needs a WSGI object returned to run properly.
def gunicorn_app():
    # Spawn your subprocess, wait 5 seconds to ensure gunicorn is initialized.
    eventlet.spawn_after(5, emit_event_periodically, TIMEOUT)
    print("Spawned Process")
    # return the flask app to run.
    return react_app
   
# If you run python server.py this will run.
if __name__ == '__main__':
    start_server()