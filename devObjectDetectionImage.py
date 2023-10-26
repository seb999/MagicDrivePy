import numpy as np
import cv2
import tensorflow as tf
from picamera2 import Picamera2
import time
import threading

#--------------------------TENSORFLOW----------------------
# Load the TFLite model
interpreter = tf.lite.Interpreter(model_path='Model/lite-model_efficientdet_lite0_detection_default_1.tflite')
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
imh = input_details[0]['shape'][1]
imw = input_details[0]['shape'][2]

# use the label map to get human-readable class names
with open('labelmap.txt', 'r') as f:
    label_map = f.read()
label_map = label_map.split('\n')

# ---------------TEST WITH IMAGE--------------------------------------------
# input_image = cv2.imread('voiture.jpg')
# input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)  # Convert to RGB format
# input_image = cv2.resize(input_image, (448, 448))  # Resize to match model input size
# input_image = np.expand_dims(input_image, axis=0)
# # input_image = (input_image.astype('float32') / 255.0)

# # Set the input tensor
# interpreter.set_tensor(input_details[0]['index'], input_image)
# interpreter.invoke()

# # Get the output tensor details
# num_detections = int(interpreter.get_tensor(output_details[3]['index']))
# detection_boxes = interpreter.get_tensor(output_details[0]['index'])
# detection_classes = interpreter.get_tensor(output_details[1]['index'])
# detection_scores = interpreter.get_tensor(output_details[2]['index'])

# # Post-process the results
# detection_boxes = detection_boxes[0, :num_detections]
# detection_classes = detection_classes[0, :num_detections].astype(np.uint8)
# detection_scores = detection_scores[0, :num_detections]

# # Print the detected objects
# for i in range(num_detections):
#     if detection_scores[i] > 0.5:  # You can adjust the confidence threshold
#         class_id = int(detection_classes[i])
#         class_name = label_map[class_id]
#         box = detection_boxes[i]
#         ymin, xmin, ymax, xmax = box
#         print(f"Class: {class_name}, Score: {detection_scores[i]}, Bounding Box: {ymin, xmin, ymax, xmax}")

# -------------------------------------------------------------------------

#------------------INIT CAMRA------------------------------------------
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (448, 448)}))
picam2.start()
picam2.set_controls({"AfMode": 2, "LensPosition": 425})
cv2.startWindowThread()

# Create a flag to control the inference loop
inference_running = True

# List to store detected rectangles and labels
detected_objects = []

# Function to perform inference
def inference_thread():
    while inference_running:
        frame = picam2.capture_array()
        im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        im = cv2.resize(im, (imw, imh)) 
        im = np.expand_dims(im, axis=0)

         # Create an empty frame for drawing rectangles
        output_frame = frame.copy()
    
      
        # Get the output tensor details
        num_detections = int(interpreter.get_tensor(output_details[3]['index']))
        detection_boxes = interpreter.get_tensor(output_details[0]['index'])
        detection_classes = interpreter.get_tensor(output_details[1]['index'])
        detection_scores = interpreter.get_tensor(output_details[2]['index'])

        # Set the input tensor
        interpreter.set_tensor(input_details[0]['index'], im)
        interpreter.invoke()
        
        detected_objects.clear()  # Clear the list of detected objects

        if num_detections > 0:
            # Post-process the results
            detection_boxes = detection_boxes[0, :num_detections]
            detection_classes = detection_classes[0, :num_detections].astype(np.uint8)
            detection_scores = detection_scores[0, :num_detections]
    
        # loop throw objects detected
        for i in range(num_detections):
            if detection_scores[i] > 0.7:  # You can adjust the confidence threshold
                class_id = int(detection_classes[i])
                class_name = label_map[class_id]
                box = detection_boxes[i]
                ymin, xmin, ymax, xmax = box
                print(f"Class: {class_name}, Score: {detection_scores[i]}, Bounding Box: {ymin, xmin, ymax, xmax}")

                # Draw a rectangle around the object
                #ymin, xmin, ymax, xmax = int(ymin * imh), int(xmin * imw), int(ymax * imh), int(xmax * imw)
                #cv2.rectangle(output_frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)  # Green rectangle

                # Add a label near the rectangle
                #label = f"{class_name}: {detection_scores[i]:.2f}"
                #cv2.putText(output_frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # Green text
                
                 # Add the detected object to the list
                detected_objects.append((class_name, ymin, xmin, ymax, xmax))

        
        #time.sleep(0.05)

# Start the inference thread
inference_thread = threading.Thread(target=inference_thread)
inference_thread.start()

# Display the camera frame
while True:
    frame = picam2.capture_array()
    for obj in detected_objects:
        
        class_name, ymin, xmin, ymax, xmax = obj
        
        ymin, xmin, ymax, xmax = int(ymin * imh), int(xmin * imw), int(ymax * imh), int(xmax * imw)
        
        # Draw a rectangle around the object
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)  # Green rectangle

        # Add a label near the rectangle
        label = f"{class_name}"
        cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # Green text


    cv2.imshow("Camera", frame)
    cv2.waitKey(1)
