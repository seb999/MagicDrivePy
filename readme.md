### Activate Environement ###


### Documentation ###

    0 - Give full access 777 to images and folders right / left / center
        cd right
        subo chmod 777 *
        cd left
        subo chmod 777 *
        cd center
        subo chmod 777 *

    1 - run python script 0 - uploadToHF.py that will do :
        -add extension jpg to each images
        -resize images to 254 pixcels
        -create or update the csv file for Hugginge Face : 
            the images in folder right / left / center will be merge in folder all
            if new images added in one of those folder, they will be added to the all folder
        -upload images and csv to Hugginge face

    2 - training the model is done on the macmini

    3 - launch scripts _magicDriveServer.py and _magicDriveStreaming.py to stream and inference the model previously created
