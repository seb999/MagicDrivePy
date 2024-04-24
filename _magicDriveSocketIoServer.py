import socketio
import eventlet

# Create a Socket.IO server instance
sio = socketio.Server(cors_allowed_origins="*")  # Set CORS options here

# Define an event handler for the "connect" event
@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")
    
    # Send a "Hello, World!" message to the newly connected client
    # sio.emit("message", "Hello, World!", room=sid)

# Define an event handler for the "message" event
@sio.event
def message(sid, data):
    print(f"Message from {sid}: {data}")
    # Broadcast the message to all connected clients (including the sender)
    sio.emit("message", data)

# Define an event handler for the "disconnect" event
@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

if __name__ == "__main__":
    app = socketio.WSGIApp(sio)
    eventlet.wsgi.server(eventlet.listen(("127.0.0.1", 5000)), app)
