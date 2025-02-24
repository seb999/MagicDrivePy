import requests

# URL to the raw file on GitHub
url = 'https://huggingface.co/Seb0099/autopilot-car-model/blob/main/model.tflite'

# Send a GET request to download the model
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Save the model file to the current directory
    with open('model.tflite', 'wb') as file:
        file.write(response.content)
    print("model.tflite downloaded and saved successfully.")
else:
    print(f"Failed to download the file. Status code: {response.status_code}")
