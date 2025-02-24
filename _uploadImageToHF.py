import os
from pathlib import Path
import requests
from io import BytesIO
from PIL import Image
from huggingface_hub import HfApi, create_repo, upload_file, login
import pandas as pd
from pathlib import Path
import json
import shutil

HF_USERNAME = "Seb0099"  # Replace with your Hugging Face username
DATASET_REPO = "autopilot-dataset-pictures"  # Dataset repo name
user_profile = os.path.expanduser("~")

base_path = os.path.join(user_profile, "Pictures")
folders = ['center', 'left', 'right']
jsonl_file_path = os.path.join(base_path, "image_data.jsonl")

###############################
#  Add jpg extension to images
###############################
def rename_image_withExtension():
    for folder in folders:
        folder_path = os.path.join(base_path, folder)

        # Check if the folder path exists
        if os.path.exists(folder_path):
            # Loop through all files in the folder
            for filename in os.listdir(folder_path):
                # Join the folder path and file name to get the full file path
                full_file_path = os.path.join(folder_path, filename)
                
                # Check if the item is a file
                if os.path.isfile(full_file_path):
                    
                    # Get the file extension
                    file_name, file_extension = os.path.splitext(filename)
                    
                    # Check if the file does not already have a ".jpg" extension
                    if file_extension != ".jpg":
                        # Rename the file with the ".jpg" extension
                        new_file_path = os.path.join(folder_path, file_name + ".jpg")
                        os.rename(full_file_path, new_file_path)
                        print(f"Renamed {filename} to {file_name}.jpg")
            
            print("All files have been renamed to have a '.jpg' extension.")
        else:
            print(f"Folder not found at '{folder_path}'")   

###########################################
#  Resize images
###########################################
def resize_image(target_width=None, target_height=224):
   for folder in folders:
        folder_path = os.path.join(base_path, folder)

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            # Check if the file is an image
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                try:
                    with Image.open(file_path) as img:
                        # Get original dimensions
                        original_width, original_height = img.size


                        # Calculate target dimensions while maintaining aspect ratio
                        if target_width is not None:
                            aspect_ratio = original_height / original_width
                            calculated_height = int(target_width * aspect_ratio)
                            calculated_width = target_width
                        elif target_height is not None:
                            aspect_ratio = original_width / original_height
                            calculated_width = int(target_height * aspect_ratio)
                            calculated_height = target_height
                        else:
                            raise ValueError("Either target_width or target_height must be specified.")


                        # Skip resizing if the image already matches the target dimensions
                        if (original_width == calculated_width and original_height == calculated_height):
                            print(f"Skipping already resized image: {file_path}")
                            continue

                        # Resize the image
                        resized_img = img.resize((calculated_width, calculated_height), Image.Resampling.LANCZOS)

                        # Overwrite the original image
                        resized_img.save(file_path)
                        print(f"Resized and replaced: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_name}: {e}")
            else:
                print(f"Skipped non-image file: {file_name}")

###########################################
# Create JSONL or update it 
###########################################
def create_image_jsonl():
    with open(jsonl_file_path, 'w') as jsonl_file:
        for folder in folders:
            folder_path = os.path.join(base_path, folder)
            
            # Check if the folder exists
            if not os.path.exists(folder_path):
                print(f"Folder {folder} not found.")
                continue
                
            for filename in os.listdir(folder_path):
                # Filter out non-image files if needed
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_data = {
                        "file_name": filename,
                        "folder": folder
                    }
                    # Write to the .jsonl file
                    jsonl_file.write(json.dumps(image_data) + '\n')
    
    print(f"JSONL file created at: {jsonl_file_path}")

###########################################
#  Upload to Hugginge Face (take each image in jsonl and upload then)
###########################################
def upload_dataset_to_hf():     
    # ---------------------------------------------
    # Step 1: Create Hugging Face Dataset
    # ---------------------------------------potentionetre
    # ------
 
    api = HfApi()
    api.create_repo(repo_id=f"{HF_USERNAME}/{DATASET_REPO}", repo_type="dataset", exist_ok=True)

    # ------------------------------
    # Step 2: Upload Images to HF
    # ------------------------------
    if os.path.exists(jsonl_file_path):
        # Load the JSONL file
        with open(jsonl_file_path, 'r') as file:
            jsonl = [json.loads(line) for line in file]

        for row in jsonl:
            file_name = row['file_name']
            image_path = os.path.join(base_path, row['folder'], file_name)

            # Check if the image exists before uploading
            if os.path.exists(image_path):
                upload_file(
                    path_or_fileobj=image_path,
                    path_in_repo=f"images/{file_name}",
                    repo_id=f"{HF_USERNAME}/{DATASET_REPO}",
                    repo_type="dataset"
                )
                print(f"✅ Uploaded: {file_name}")
            else:
                print(f"❌ Image not found: {file_name}")
    else:
        print(f"❌ JSONL file not found at {jsonl_path}")

    # -------------------------------------------
    # Step 3: Upload the JSONL file HF
    # -------------------------------------------
    if os.path.exists(jsonl_file_path):
        upload_file(
            path_or_fileobj=jsonl_file_path,
            path_in_repo="images/metadata.jsonl",
            repo_id=f"{HF_USERNAME}/{DATASET_REPO}",
            repo_type="dataset"
        )

        print("✅ JSON dataset uploaded to Hugging Face!")
    else:
        print("❌ JSON file not created.")
    print("🎉 All images uploaded successfully!")

#rename_image_withExtension()
#resize_image(target_height=224)rdp
#create_image_jsonl()t

upload_dataset_to_hf()
