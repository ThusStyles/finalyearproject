# Convolutional Neural Network For Ground Truthing

This software uses convolutional neural network and aims to generate a ground truth set in the smallest time possible with a minimum number of human interactions.

#Features
- Import a folder of images to classify
- Create an aribtrary number of sets from images
- Convolutional neural network to train on sets
- Move items between sets once classified
- Save\Load sets of images
- View reports on how the sets and how the network is performing
- Change various settings such as the number of iterations or learning rate

# Screenshots
![Initial interface](design1.png?raw=true "Initial interface")
![Importing a folder of images](design2.png?raw=true "Importing a folder of images")
![Creating sets](design3.png?raw=true "Creating sets")
![Images classified](design5.png?raw=true "Images classified")
![Sets created](design4.png?raw=true "Sets created")
![Reports section](design6.png?raw=true "Reports section")
![Settings section](design7.png?raw=true "Settings section")


# Installation Instructions

Several libraries are required to run the software, and are outlined below:

- Python 3.6 - https://www.python.org/downloads/
- Tensorflow (pip recommended) - https://www.tensorflow.org/install/
- PyQt5 (pip recommended) - http://pyqt.sourceforge.net/Docs/PyQt5/installation.html
- numpy + matplotlib (pip recommended) - https://www.scipy.org/install.html
- PIL - https://pillow.readthedocs.io/en/latest/installation.html
    
Then run the following to start the application:
 ```sh
$ cd Framework
$ python __init__.py
```
