import cv2
from picamera2 import Picamera2
import numpy as np
import tensorflow as tf
from PIL import Image
import socketio
import threading
import time
import sys 
import json 

labels = ["center", "left", "right"] 

# Create a Socket.IO client instance
sio = socketio.Client()

# Connect to the magicDrive Socket.IO server
try:
    sio.connect("http://127.0.0.1:5000")
except socketio.exceptions.ConnectionError as e:
    print(f"SOCKET.IO SERVER NOT RUNNING")
    sys.exit(0)

def preprocess_image(image, height, width):
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (width, height))   # Resize the image to match the input size of the model
    image = image.astype(np.float32) / 255.0   # Cast to FLOAT32 and normalize pixel values to [0, 1]
    image = np.expand_dims(image, axis=0)  # Add a batch dimension
    return image

# Load the TensorFlow Lite model
interpreter = tf.lite.Interpreter(model_path='/home/sebastien/Git/MagicDrivePyService/Model/model.tflite')
interpreter.allocate_tensors()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()
time.sleep(5)
picam2.set_controls({"AfMode": 2, "LensPosition": 425})

cv2.startWindowThread()

# Create a flag to control the inference loop
inference_running = True

# Function to perform inference
def inference_thread():
    while inference_running:
        im = picam2.capture_array()
  
        # Perform inference using the TensorFlow Lite model
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]
        processed_image = preprocess_image(im, height, width)
        interpreter.set_tensor(input_details[0]['index'], processed_image)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])

        # Find the index of the label with the highest score
        predicted_label_index = np.argmax(predictions)
        predicted_label = labels[predicted_label_index]
        predicted_score = float(predictions[0][predicted_label_index]) 

        prediction_result = {
            "label": predicted_label,
            "score": predicted_score
            }
        
        print(prediction_result)

        # Send the JSON result to the Socket.IO server
        sio.emit("message", json.dumps(prediction_result))

        # Introduce a delay to control the inference frequency (e.g., 1 frame per second)
        time.sleep(0.07)  # Sleep for 1 second (adjust the value as needed)

# Start the inference thread
inference_thread = threading.Thread(target=inference_thread)
inference_thread.start()

# Display the camera frame
while True:
    im = picam2.capture_array()
    #cv2.imshow("Camera", im)
    # Break the loop and release resources if the window is closed
    if cv2.waitKey(1) & 0xFF == 27:  # 27 is the ASCII code for the 'Esc' key
        inference_running = False
        break

# Release resources
cv2.destroyAllWindows()
picam2.stop()
