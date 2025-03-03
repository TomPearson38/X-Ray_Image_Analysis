# X-Ray_Image_Analysis

This program has been created in collaboration with the Universty of Sheffield and AMRC Castings.
It contributes to the dissertation project created by @TomPearson38

The system has been coded in Python and allows the user to provide an image of an X-rayed alloy to be analysed. The system then
detects faults in the provided image and provides feedback and a confidence score on the areas it believes contain faults. The user is
then able to judge the performance of the system and either correct it or confirm that it is correct. The image has the option to be added to
the dataset to retrain the AI at a later date and improve its functionality

# Requirements

The requirements.txt file contains all the required pip packages for the project.
The yolov5 repository is also required to make the program function. https://github.com/ultralytics/yolov5