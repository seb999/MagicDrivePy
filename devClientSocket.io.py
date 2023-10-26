import socketio

# Create a Socket.IO client instance
sio = socketio.Client()

# Define an event handler for the "message" event
@sio.on("message")
def message(data):
    print(f"Server: {data}")

# Connect to the Socket.IO server
sio.connect("http://127.0.0.1:5000")  # Adjust the server URL as needed

# Send a message to the server
while True:
    user_input = input("Enter a message (or 'exit' to quit): ")
    if user_input.lower() == "exit":
        break
    sio.emit("message", user_input)

# Disconnect from the server
sio.disconnect()
