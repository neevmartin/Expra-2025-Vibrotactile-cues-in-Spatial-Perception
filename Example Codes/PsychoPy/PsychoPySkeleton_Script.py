# --------------------------------------
# General information
# --------------------------------------
# This is a sekelton script for psychopy which already consists of some key features, like drawing a cursor, drawing shapes, etc.
# It consists of a block- and trialwise structure and logs data.

# --------------------------------------
# Import libraries
# --------------------------------------
from psychopy import visual, event, core
import numpy as np
import pandas as pd
import os
import sys
import time
# --------------------------------------
# Main Setup
# --------------------------------------
# Sets working directory to current script folder
os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

# Flow control
isRunning = True
isFirstDown = False

# Creating objects
winSize = np.array([1280,720]) # windows size in which the experiment will run 
colorBlack = [-1, -1, -1] # color in psychopy is -1 = black, 0 = medium grey, 1 = white


# --------------
# Introduce participant ID
# --------------
participantID = input("\n=-----------------------------------------=\n" + "Introduce participant's ID: " + "\n=-----------------------------------------=\n" + "ID:")
participantID = "s_" + participantID # this is arbitrary, can be any input/string

# --------------
# Get experiment timestamp
# --------------
creationTime = time.strftime("%H_%M_%S")

# --------------
# Does data folder exist? 
# If not create it
# --------------
os.makedirs(os.path.dirname(__file__)+"/data", exist_ok=True)

# --------------
# Does participant's folder exist? 
# If not create it
# --------------
participant_folder = os.path.dirname(__file__)+"/data/"+ participantID
os.makedirs(participant_folder, exist_ok=True)



# Defining window and some objects
# ALERT!: Never use fullscreen while debugging. 
# Closing the window is very annoying. 
myWin = visual.Window(size=winSize, color=colorBlack, pos=[0,0], units='pix', fullscr=False) # window
myInstr = visual.TextStim(myWin, text="Please click 4 times in this window", pos=(0, winSize[1]/2-50)) # instructions
myRect =  visual.Rect(myWin, width=75, height=winSize[1]/4, units="pix", pos=[0, 0]) # rectangle 
myMouse = event.Mouse(visible=False) # mouse object
myClick = visual.TextStim(myWin, text="Click Nr: ", pos=(0, winSize[1]/2-200)) # text for clicks
myTime = visual.TextStim(myWin, text="Time: ", pos=(0, winSize[1]/2-250)) # Text for timestamp of click
myCursor = visual.Circle(myWin, radius=10, pos=(0,0), fillColor=(1,0,0)) # Cursor appearance

# Time-related bits
myTimer = core.Clock() # creates a timer
def getDT(): # function to update time
    dt = myTimer.getTime() 
    myTimer.reset() # resets time
    return dt


# Quit the experiment if conditions are met
def myQuit():
    keys = event.getKeys()
    if keys:
        # q quits the experiment
        if keys[0] == 'q':
            myWin.close()
            core.quit()
        # esc quits the experiment
        if keys[0] == "escape":
            myWin.close()
            core.quit()


# --------------------------------------
# Initial screen
# --------------------------------------
initialInstructions = visual.TextStim(myWin, text="Welcome to your first experiment script! \n Press the mouse to continue", pos=(0, 0)) # instructions

while True:
    # Get button input
    buttons = myMouse.getPressed()[0]
    initialInstructions.draw() # draw the objet you want the be shown
    myWin.flip() # flip makes the drawn objects appear in the screen 

    # Always introduce a way to close the script for security reasons
    myQuit()

    # If any button presss detected
    if buttons:
        break

## Wait 0.5 s after button press
core.wait(0.5)

# --------------------------------------
# Experimental part
# --------------------------------------
timeElapsed = 0                         # Time elapsed since the beginning of the experiment
trialt = 0                              # Trial time elapsed

counter = 0                             # Repetition counter
maxClicks = 4                           # Max clicks allowed per block

currentBlock = 0                        # Sets current block
maxBlocks = 2                           # Max blocks allowed

isFirstDown = False                     # Flag: Is this the first time mouse was clicked?

writeData = True                        # Do you want to save the data afterwards?
data = pd.DataFrame(columns = ["Id", "BlockNr", "Clickcount", "Time"]) # data frame being created which stores the data
# be careful with dataframes on the fly: they are computationally heavy to write into

# Running experiment here:
while isRunning:
    if currentBlock < maxBlocks: 
        # Add timer function here
        dt = getDT()
        timeElapsed += dt 
        trialt += dt

        # Place mouse
        posX, posY = myMouse.getPos()
        myCursor.setPos((posX,posY)) 

        # Get cutton input
        buttons = myMouse.getPressed()[0]

        # If any button presss detected
        if buttons:
            # IsFirstDown makes sure to only get 1 measure each button press
            if not isFirstDown:
                # Button was pressed for the first time in this frame
                isFirstDown = True

                # Display click number
                myClick.setText("Block Nr: %i;  Click Nr: %i" % (currentBlock, counter + 1))

                # Display when the button was clicked
                myTime.setText("Time: %.4f" % ((trialt)))
                myTime.draw()

                # Save current data to store 
                currentLine = pd.DataFrame([[participantID, currentBlock, counter, trialt]], columns = ["Id", "BlockNr", "Clickcount", "Time"])

                # Concatenate with our trial-by-trial dataframe 
                data = pd.concat([data, currentLine], ignore_index = True)
                
                # Add 1 to our "trial" counter
                counter += 1
                
                # Reset trial time
                trialt = 0
                # If counter equals maxClicks -> new block
                if counter >= maxClicks:
                    # New block
                    currentBlock += 1
                    # Reset counter
                    counter = 0
        else:
            isFirstDown = False

        # Draw instructions only first block & first trial
        if counter == 0 and currentBlock == 0:
            myInstr.draw()
        ## Then, draw click nr. and time
        else:
            myClick.draw()
            myTime.draw()

        # Draw remaining elements
        # Note: What happens if we change the order?
        myRect.draw() 
        myCursor.draw()

        # Window flip -> Shows in screen previously drawn objects
        myWin.flip()

        # Always introduce a way to close the script for security reasons
        myQuit()
    elif currentBlock >= maxBlocks:
        isRunning = False

# --------------------------------------
# Save data
# --------------------------------------
# Note that by introducing the creation time at second precision
# it is *almost* impossible to create the same dataframe 2 times
# Thus, we do not have to worry about overwritting
data.to_csv(os.path.dirname(__file__)+"/data/"+ participantID + '/myData_%s.csv' % (creationTime))
core.wait(0.5)

# --------------------------------------
# Final screen
# --------------------------------------
finalMessage = visual.TextStim(myWin, text="Thank you for your participation! \n Your data was correctly stored!", pos=(0, 0)) # instructions

while True:
    # Get cutton input
    buttons = myMouse.getPressed()[0]
    finalMessage.draw()
    myWin.flip()

    # Always introduce a way to close the script for security reasons
    myQuit()

    # If any button presss detected
    if buttons:
        break

# --------------------------------------
# Close experiment
# --------------------------------------
myWin.close() # closes the window
core.quit() # closes script instance
