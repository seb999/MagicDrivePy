import os

folder_path = "/home/sebastien/Pictures/center"

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
