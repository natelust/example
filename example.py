#lets import the nessisary
try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

import numpy as np

#Every plugin is a class, it must be a subcalss of a QWidget but may inherit
#other classes. These could be layouts created with qt designer and pyuic4
#see other plugins for more details
class example(QWidget):
    def __init__(self,main,parent=None):
        #create an init function, this is called when the plugin is created and
        #should handel setting up all the GUI elements
        #Also must initiate the classes we inherit from
        QWidget.__init__(self,parent=parent)
        #The plugin will always be passed main, a referance to the main program
        #here we save it to self to reuse it outside the init function
        self.main = main

        #The following section we will create the layout and all the logic for
        #the example in pure python for learning purposus. We STRONGLY recommend
        #using QT Designer to create a layout, there are less errors, and the
        #design is separated from the logic

        #here we set a good size for the initial size of our plugin, all sizing
        #should be handeled in the plugin
        self.widget_size = QRectF(0,0,300,300)
        #We create an instance of a virtical container, this will lay out added
        #widgets on top of each other.
        self.vbox = QVBoxLayout()
        #We set the alignment to try and put everything towards the center, as it
        #is more visually apealing
        self.vbox.setAlignment(Qt.AlignCenter)
        #create a button instance which will function as initiating the squaring
        #of the image
        self.square_button = QPushButton()
        #set the text of the button
        self.square_button.setText('Square')
        #create a label for the square button
        self.square_label = QLabel()
        #set the text for the label
        self.square_label.setText('This will square image intensities')
        #same with a square root button
        self.sqrt_button   = QPushButton()
        #set sqrt button text
        self.sqrt_button.setText('Sqrt')
        #create sqrt label
        self.sqrt_label = QLabel()
        #set the text for the sqrt label
        self.sqrt_label.setText('This will sqrt image intensities')
        #add the widgets to the layout in the order that you want them in
        self.vbox.addWidget(self.square_label)
        self.vbox.addWidget(self.square_button)
        self.vbox.addWidget(self.sqrt_label)
        self.vbox.addWidget(self.sqrt_button)
        #now we want to set the layout for our widget as our vbox
        self.setLayout(self.vbox)
        #For demonstrative purposus we do not want the user to be able to sqrt
        #the image until it has been squared, so we set sqrt button inactive
        self.sqrt_button.setEnabled(False)
        #now connect each button to the function which is called when the user
        #clicks on it
        self.connect(self.square_button,SIGNAL('clicked()'),self.square_image)
        self.connect(self.sqrt_button,SIGNAL('clicked()'),self.sqrt_image)
        #finally we are going to create a constant to know the state of
        #manipulation to use on exit
        self.issquared = False
        #finally we connect to the parent 'closing' signal to trigger the close event
        #when the parent dock widget is destroied
        self.connect(parent,SIGNAL('closing'),self.close)

    def square_image(self):
        #here is where we actually square the image
        #we should keep track of the sign of the pixels since squaring will destroy
        #this information
        self.signs = np.sign(self.main.imageedit)
        #we use the referance to the primary program we got passed and then saved
        #here the imageedit variable in the main program is the image that is
        #currently being displayed ith any other manipulations applied
        self.main.imageedit = self.main.imageedit**2
        #we now wany to also square the white and black points of the scaling
        self.main.white = self.main.white**2
        self.main.black = self.main.black**2
        #Conversly we could have set the gray point and contrast and called the
        #create black and white function, but this is more straitforward
        #now we want to update the canvas in the main application
        self.main.update_canvas()
        #we now turn on the square root button
        self.sqrt_button.setEnabled(True)
        #disable the square button just so the user can only toggle back and forth
        #between the two states
        self.square_button.setEnabled(False)
        #findally set the is squared property to true, indicating it has been squared
        self.issquared = True

    def sqrt_image(self):
        #in this function we can reverse the square of the image by taking a square root
        #it is only available after the image has been squared
        self.main.imageedit = self.main.imageedit**0.5
        #we should check for any values that are not finite and set them to zero
        #just to be sure
        self.main.imageedit[np.isfinite(self.main.imageedit)==False] = 0
        #multiply the sign of the image back
        self.main.imageedit = self.signs * self.main.imageedit
        #now set the black and white values
        self.main.white = self.main.white**0.5
        self.main.black = self.main.black**0.5
        #update and redraw the canvas
        self.main.update_canvas()
        #set square button back to active and deactivate sqrt, just so you can only
        #toggle back and forth
        self.square_button.setEnabled(True)
        self.sqrt_button.setEnabled(False)
        #set the is squared button back to False
        self.issquared = False

    def closeEvent(self,event):
        #Finally we are overloading the function that will be called when the widget is
        #closed, it is a default part of any QWidget. This allows us to execute any
        #cleanup code we want, in this case making sure the image is back where it started
        #we want to check if the image is squared, if it is square root it.
        #we do not need to check if it is squarerooted, because activating and deactivating
        #the buttons only allows squaring to happen first
        if self.issquared:
            self.sqrt_image()
        #This step says that we accpet the close event and process it.
        #by not accepting some platforms will not close the widget
        event.accept()

    def register_functions(self=None):
        #Note setting defualt value for self, this is very very important, other wise the
        #function will fail register properly!!!

        #This function is called by the listener thread in the main program. Its purposus
        #is to register what functions can be called from an embeded session inside an
        #interpreted language, such as python. This function does not have to be implimented
        #the listener will only call it if it is present in a plugin, but if you want your
        #plugin to be used from an interpreted session it must be present.
        #This function should return 3 lists of strings
        #the first list should be the name used to identify the function from the interpreter
        #try to pick somewhat unique and identifying names
        names = ['square_plugin_square','square_plugin_sqrt']
        #the next variabel should contain a list of descriptions, letting the user know what
        #the function does, and if it expects arguments and how to format them. All arguments
        #will be passed in as a list, so a description would be like args: [var1,var2] where
        #var one is a float and var2 is a 2d array. The functions in this example take no
        #arguments
        descriptions = ['square the image desplayed, expects no arguments',\
                        'take the square root of the image desplayed, expects no arguments']
        #finally there should be a list of strings corresponding to the function to be called
        #in the plugin class
        functions = ['square_image','sqrt_image']
        return names,descriptions,functions
