# Install Instructions

To ensure that the program works correctly, you must first follow these steps on how to install the program.

**Video Tutorial**
This text guide assumes that the install process goes smoothly, if you would like a commentated video demonstrating each step from scratch, watch this video instead. [Link to Video](https://youtu.be/3IbNj0MY_do)

## Python Installation
This program needs python version 3.12. (It was developed using python 3.12.8, but the newest version of python 3.12 should be sufficient). This can be downloaded from python at [Python Homepage](https://www.python.org/downloads/windows/). With the latest version at the time of writing being, [3.12.10](https://www.python.org/downloads/release/python-31210/).

When installing ensure that you select the **Add Python.exe to Path** option at the bottom of the installer.

## Git Installation
This program was developed using Git. Git is an open source tool used for repository management and distribution. It will be how you "clone" the source code and how you access other programs you need. In order to do this, you will need to install [Git for Windows](https://git-scm.com/downloads/win), or any other git management tool.

## Cloning the repository
The repository contains the code relating to the system. This is available [here](https://github.com/TomPearson38/X-Ray_Image_Analysis). To download it onto your system select the green clone button on the page, then HTTPS, then copy the link. The open a file explorer window where you would like to clone your code. Right click and open Git Bash here. Type `git clone URL` with URL being the URL you just copied. Press enter and it should download the code to your computer. Do not close the git bash window as it is needed for the next step.

For a more detailed guide visit this one by GitHub, [Webpage](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

## Cloning YOLOv5
In a similar way to how we cloned the previous Git project, YOLOv5 needs to be cloned from [here](https://github.com/ultralytics/yolov5). This should be cloned into the same folder your git bash window was in before. Follow the same steps and clone the repository.

Now, open a command prompt terminal and navigate to the yolov5 folder. This can be done by clicking the path at the top of the file explorer window and typing in 'cmd'. There are more details available on this [website](https://www.wikihow.com/Change-Directories-in-Command-Prompt).

Type in the command `pip install -r requirements.txt`. This will install all the requirements for YOLOv5.

## Installing X-Ray Image Analysis Requirements
Navigate to the X-Ray Image Analysis folder and launch the `installer.bat`. Windows may warn you about a potentially dangerous file, this is because bat files can be used for malicious intent as they run commands, however this one is used to install the dependencies for the program.

Once that has finished, you can run the program by clicking on the `start_program.bat` file.

## (Extra) Bat File Help

If you are unable to launch bat files, you can still launch them manually. If you are able to launch them successfully, ignore this section.

First, navigate to the location of the bat file in a command prompt window.
Then in a file explorer window, right click the bat file and select edit. Copy the file's contents line by line and enter each one into the command window that you opened previously.