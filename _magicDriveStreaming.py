import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
import socketio
import threading
import time
import sys 
import json 
from picamera2 import Picamera2

labels = ["center", "left", "right"] 

# Create a Socket.IO client instance
sio = socketio.Client()

# Attempt to connect to the server with retries
connected = False
while not connected:
    try:
        sio.connect("http://127.0.0.1:5000")
        connected = True
    except socketio.exceptions.ConnectionError:
        print("SOCKET.IO SERVER NOT RUNNING, RETRYING IN 5 SECONDS...")
        time.sleep(5)

# Preprocess function
def preprocess_image(image, height, width):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    image = cv2.resize(image, (width, height))  # Resize
    image = image.astype(np.float32) / 255.0  # Normalize
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

# Load the TensorFlow Lite model
interpreter = tf.lite.Interpreter(model_path='/home/sebastien/Git/MagicDrivePy/model/model.tflite')
interpreter.allocate_tensors()

# Initialize PiCamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()
time.sleep(5)

# Set auto-focus (remove manual lens position)
picam2.set_controls({"AfMode": 2})

# Control flag for inference loop
inference_running = True

# Inference function with adaptive FPS
def inference_thread():
    while inference_running:
        start_time = time.time()

        im = picam2.capture_array()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        height, width = input_details[0]['shape'][1], input_details[0]['shape'][2]
        processed_image = preprocess_image(im, height, width)

        interpreter.set_tensor(input_details[0]['index'], processed_image)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])

        predicted_label_index = np.argmax(predictions)
        predicted_label = labels[predicted_label_index]
        predicted_score = float(predictions[0][predicted_label_index])

        prediction_result = {
            "label": predicted_label,
            "score": predicted_score
        }
        print(prediction_result)

        # Send result via Socket.IO
        sio.emit("message", json.dumps(prediction_result))

        # Adjust FPS dynamically
        elapsed_time = time.time() - start_time
        time.sleep(max(0, 0.3 - elapsed_time))  # Aim for ~10 FPS

# Start the inference thread
thread = threading.Thread(target=inference_thread)
thread.start()

# Display camera feed
while inference_running:
    im = picam2.capture_array()
    cv2.imshow("Camera", im)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC key to exit
        inference_running = False
        break

# Cleanup resources
thread.join()  # Ensure the thread stops
cv2.destroyAllWindows()
picam2.stop()
