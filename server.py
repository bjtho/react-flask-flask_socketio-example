'''
SocketIO Implementation + entrypoint.
'''

PORT = 9999 # Both flask, and socketio will listen on this port.
TIMEOUT = 1 # Timeout for the subprocess function.

# hello again monkey
import eventlet
eventlet.monkey_patch()


from app import socketio, react_app
from flask import request

msg_q = eventlet.Queue()
# do your server route stuff here.
@socketio.on('connect')
def handle_connect(*args):
    # do connection things
    print(f"Client is connected.")


@socketio.on('disconnect')
def handle_disconnect(*args):
    # do disconnection things.
    print("Client is disconnected.")
    
@socketio.on('my_topic')
def handle_my_topic(data):
    # note, not a great idea to use the sid as its ephemeral.
    q_item = {'sid': request.sid, 'msg': data.get('msg') or ''}
    msg_q.put(q_item)

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
    

    
    while True:
        # do stuff.
        if not msg_q.empty():
            msg = msg_q.get()
            print(msg['sid'], msg['msg'])
            socketio.emit('other_topic', {'data': f"Hello {msg['sid']}, thanks for your message."})
        
        # you need to let the thread sleep in order to give up control and handle other things as we are using 'green threads'.
        # This may not scale super well, and I am not sure what the minimum amount of time can be to sleep a thread.
        eventlet.sleep(n)

# Normal, windows 10 compatable runtime. This is what I use for development because it's a PITA
# to constantly build to Docker for every little change.
def start_server():
    # spawn your subprocess..
    eventlet.spawn(emit_event_periodically, TIMEOUT)

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