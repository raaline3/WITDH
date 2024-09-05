# WITDH Beta 0.6
# Version Notes: Functioning build, ready for feedback

# Import
import pygame
from pygame.locals import *
import sys
import csv
import math
import os
pygame.init()
FPS = 60
fpsClock = pygame.time.Clock()
running = 1

# Change These ----------------------------------------------------------------------------
# In pixels
screenWidth = 1000
screenHeight = 660

fieldWidth = 500
fieldHeight = 500
# In inches
robotLength = 18 
robotWidth = 18
# ------------------------------------------------------------------------------------------

# Constants
Black = (0,0,0)
White = (255,255,255)
Red = (255, 0, 0)
Green = (0, 200, 0)
Blue = (0, 0, 255)
Yellow = (255, 255, 0)

pixel_per_inch = fieldWidth/144

robotLength *= pixel_per_inch
robotWidth *= pixel_per_inch

textBoxTextFont = pygame.font.Font(None, 60)
instructionTextFont = pygame.font.Font(None, 20)
labelTextFont = pygame.font.Font(None, 30)

# App Variables
clock = pygame.time.Clock() 
appState = "start pos" # Controls what the user is currently doing
selectedIndex = -1 # Index of the point that the user has selected
textboxText = ""
announcementText = "Choose a starting point"
error = False

time = 0
deltaTime = 0

file_path = "Trajectories/"

# Screen Setup
screen = pygame.display.set_mode((screenWidth,screenHeight))
screen.fill(White)

field = pygame.image.load("Images/FTC-field.png")
field = pygame.transform.scale(field, (fieldWidth, fieldHeight))
fieldRect = Rect((screenWidth - fieldWidth)/2, (screenHeight - fieldHeight)/2, fieldWidth, fieldHeight)

screen.blit(field, ((screenWidth - fieldWidth)/2, (screenHeight - fieldHeight)/2))
pygame.display.update()

# Textboxes

announcementTextBox = Rect(0,10,screenWidth,50)

inputTextBox = Rect((screenWidth/2)-screenWidth/4,screenHeight-60,screenWidth/2,50)

tfTextBox = Rect(20+screenWidth*0.25,screenHeight-60,(screenWidth/4)-50,50)
dirTextBox = Rect(screenWidth-(screenWidth/4)+50-20-screenWidth*0.25,screenHeight-60,(screenWidth/4)-50,50)
xVeloTextBox = Rect(20,screenHeight-60,(screenWidth/4)-50,50)
xPosTextBox = Rect(20,screenHeight-150,(screenWidth/4)-50,50)
yVeloTextBox = Rect(screenWidth-(screenWidth/4)+50-20,screenHeight-60,(screenWidth/4)-50,50)
yPosTextBox = Rect(screenWidth-(screenWidth/4)+50-20,screenHeight-150,(screenWidth/4)-50,50)

# Trajectory Variables
tf = [] # Time it takes to complete the motion

xPos = [] # x position
xVelo = [] # x velocity at the point

yPos = [] # y position
yVelo = [] # y velocity at the point

dir = [] # direction at the point

startingSide = ""

currentPose = 0
currentTime = 0

def generateTrajectory():
    screen.fill(White)
    screen.blit(field, ((screenWidth - fieldWidth)/2, (screenHeight - fieldHeight)/2))

    cPose = 0
    # Drawing the starting point
    if len(xPos) > 0:
        pygame.draw.line(screen, Green, (xPos[0],yPos[0]),(xPos[0]+(math.cos(math.radians(dir[0]))*50),yPos[0]+(math.sin(math.radians(dir[0]))*50)))
        pygame.draw.circle(screen, (0, 0, 0), (xPos[0], yPos[0]), 5)
    while cPose < len(tf):
        # Setting up variables
        x0 = xPos[cPose]
        xf = xPos[cPose + 1]
        xV0 = xVelo[cPose]
        xVf = xVelo[cPose + 1]

        y0 = yPos[cPose]
        yf = yPos[cPose + 1]
        yV0 = yVelo[cPose]
        yVf = yVelo[cPose + 1]

        pygame.draw.line(screen, Red, (xf,yf),(xf+xVf,yf+yVf))
        try:
            pygame.draw.line(screen, Green, (xf,yf),(xf+(math.cos(math.radians(dir[cPose+1]))*50),yf+(math.sin(math.radians(dir[cPose+1]))*50)))
        except:
            pass

        # Trajectory Generation Setup
        xA = x0
        xB = xV0
        xC = ((3 * (xf - x0))/(tf[cPose]**2)) - (((2 * xV0) + xVf)/tf[cPose])
        xD = -1*((2 * (xf - x0))/(tf[cPose]**3)) + ((xV0 + xVf)/(tf[cPose]**2))

        yA = y0
        yB = yV0
        yC = ((3 * (yf - y0))/(tf[cPose]**2)) - (((2 * yV0) + yVf)/tf[cPose])
        yD = -1*((2 * (yf - y0))/(tf[cPose]**3)) + ((yV0 + yVf)/(tf[cPose]**2))

        t = 0
        while t <= tf[cPose]:
            # Cubic Trajectory Generation 
            xP = xA + (xB * t) + (xC * (t**2)) + (xD * (t**3))
            yP = yA + (yB * t) + (yC * (t**2)) + (yD * (t**3))
            pygame.draw.circle(screen, (0, 0, 0), (xP, yP), 1)
            t += 0.005
        # Drawing the points
        pygame.draw.circle(screen, (0, 0, 0), (xf, yf), 5)
        cPose += 1
    screen.blit(textBoxTextFont.render(announcementText, False, Black), (announcementTextBox.x + 5, announcementTextBox.y + 5))
    screen.blit(textBoxTextFont.render(announcementText, False, Black), (announcementTextBox.x + 5, announcementTextBox.y + 5))
    screen.blit(instructionTextFont.render("Q to create new points", False, Black), (5, 60))
    screen.blit(instructionTextFont.render("W to run the trajectory", False, Black), (5, 75))
    screen.blit(instructionTextFont.render("E to edit points", False, Black), (5, 90))
    screen.blit(instructionTextFont.render("R to delete selected points", False, Black), (5, 105))
    screen.blit(instructionTextFont.render("T to finish and save trajectory", False, Black), (5, 120))
    pygame.display.update()

def drawTextbox(textbox, text):
    pygame.draw.rect(screen, Black, textbox, 2)
    screen.blit(textBoxTextFont.render(str(text), False, Black),  (textbox.x + 5, textbox.y + 5))
    pygame.display.flip()    

def drawAllTextboxes():
    if selectedIndex != 0:
        drawTextbox(tfTextBox, tf[selectedIndex-1])
        screen.blit(labelTextFont.render("Time", False, Black), (tfTextBox.x, tfTextBox.y - 20))
    drawTextbox(dirTextBox, dir[selectedIndex])
    screen.blit(labelTextFont.render("Direction", False, Black), (dirTextBox.x, dirTextBox.y - 20))
    drawTextbox(xVeloTextBox, xVelo[selectedIndex])
    screen.blit(labelTextFont.render("X Velocity", False, Black), (xVeloTextBox.x, xVeloTextBox.y - 20))
    drawTextbox(xPosTextBox, xPos[selectedIndex])
    screen.blit(labelTextFont.render("X Position", False, Black), (xPosTextBox.x, xPosTextBox.y - 20))
    drawTextbox(yVeloTextBox, yVelo[selectedIndex])
    screen.blit(labelTextFont.render("Y Velocity", False, Black), (yVeloTextBox.x, yVeloTextBox.y - 20))
    drawTextbox(yPosTextBox, yPos[selectedIndex])
    screen.blit(labelTextFont.render("Y Position", False, Black), (yPosTextBox.x, yPosTextBox.y - 20))

def interpolate(currentPos,startPos,ratio):
    newPos = 0
    newPos = (currentPos - startPos)/ratio
    if startingSide == "red":
        newPos *= -1
    return newPos

screen.blit(textBoxTextFont.render(announcementText, False, Black), (announcementTextBox.x + 5, announcementTextBox.y + 5))
screen.blit(instructionTextFont.render("Q to create new points", False, Black), (5, 60))
screen.blit(instructionTextFont.render("W to run the trajectory", False, Black), (5, 75))
screen.blit(instructionTextFont.render("E to edit points", False, Black), (5, 90))
screen.blit(instructionTextFont.render("R to delete selected points", False, Black), (5, 105))
screen.blit(instructionTextFont.render("T to finish and save trajectory", False, Black), (5, 120))
pygame.display.flip()
 # ____________________________________________________________________________________________________

while running:
    for event in pygame.event.get():
        # Key press
        if event.type == pygame.KEYDOWN:
            # Input textboxes
            if appState == "set tf":
                if event.key == pygame.K_RETURN:
                    try:
                        tf.append(int(textboxText))
                        if len(dir) > 0:
                            textboxText = str(dir[len(dir)-1])
                        else:
                            textboxText = "0"
                        announcementText = "Input the direction the robot is facing"
                        generateTrajectory()
                        appState = "set dir"
                        pygame.draw.rect(screen, Black, inputTextBox, 2)
                    except:
                        textboxText = "Input a number"
                elif event.key == pygame.K_BACKSPACE:
                    textboxText = textboxText[:-1]
                    generateTrajectory()
                    pygame.draw.circle(screen, (0, 0, 0), (mouseClickX, mouseClickY), 5)
                    pygame.draw.line(screen, Red, (mouseClickX,mouseClickY),(mouseReleaseX,mouseReleaseY))
                    pygame.draw.rect(screen, Black, inputTextBox, 2)
                else:
                    textboxText += event.unicode
                screen.blit(textBoxTextFont.render(textboxText, False, Black),  (inputTextBox.x + 5, inputTextBox.y + 5))
                pygame.display.flip()
            elif appState == "set dir":
                if event.key == pygame.K_RETURN:
                    try:
                        dir.append(int(textboxText))
                        textboxText = ""
                        announcementText = "Click and drag to create a new point"
                        generateTrajectory()
                        appState = "new pos"
                    except:
                        textboxText = "Input a number"
                elif event.key == pygame.K_BACKSPACE:
                    textboxText = textboxText[:-1]
                    generateTrajectory()
                    pygame.draw.circle(screen, (0, 0, 0), (mouseClickX, mouseClickY), 5)
                    pygame.draw.line(screen, Red, (mouseClickX,mouseClickY),(mouseReleaseX,mouseReleaseY))
                    pygame.draw.rect(screen, Black, inputTextBox, 2)
                else:
                    textboxText += event.unicode
                screen.blit(textBoxTextFont.render(textboxText, False, Black),  (inputTextBox.x + 5, inputTextBox.y + 5))
                pygame.display.flip()
            # Edit textboxes
            elif appState == "edit tf":
                if event.key == pygame.K_RETURN:
                    appState = "selected point"
                elif event.key == pygame.K_BACKSPACE:
                    textboxText = textboxText[:-1]
                else:
                    textboxText += event.unicode
                try:
                    if int(textboxText) > 0:
                        tf[selectedIndex-1] = int(textboxText)
                        announcementText = "Esc to deselect the point"
                    else:
                        announcementText = "Number has to be greater than 0"
                except:
                    announcementText = "Input a number"
                generateTrajectory()
                if textboxText != str(tf[selectedIndex-1]):
                    tf[selectedIndex-1] = textboxText
                    drawAllTextboxes()
                    tf[selectedIndex-1] = 1
                else:
                    drawAllTextboxes()
            elif appState == "edit dir":
                if event.key == pygame.K_RETURN:
                    appState = "selected point"
                elif event.key == pygame.K_BACKSPACE:
                    textboxText = textboxText[:-1]
                else:
                    textboxText += event.unicode
                try:
                    dir[selectedIndex] = int(textboxText)
                    announcementText = "Esc to deselect the point"
                except:
                    announcementText = "Input a number"
                generateTrajectory()
                if textboxText != str(dir[selectedIndex]):
                    dir[selectedIndex] = textboxText
                    drawAllTextboxes()
                    dir[selectedIndex] = 1
                else:
                    drawAllTextboxes()
            elif appState == "edit xVelo":
                if event.key == pygame.K_RETURN:
                    appState = "selected point"
                elif event.key == pygame.K_BACKSPACE:
                    textboxText = textboxText[:-1]
                else:
                    textboxText += event.unicode
                try:
                    xVelo[selectedIndex] = int(textboxText)
                    announcementText = "Esc to deselect the point"
                except:
                    announcementText = "Input a number"
                    
                generateTrajectory()
                if textboxText != str(xVelo[selectedIndex]):
                    xVelo[selectedIndex] = textboxText
                    drawAllTextboxes()
                    xVelo[selectedIndex] = 0
                else:
                    drawAllTextboxes()
            elif appState == "edit xPos":
                if event.key == pygame.K_RETURN:
                    appState = "selected point"
                elif event.key == pygame.K_BACKSPACE:
                    textboxText = textboxText[:-1]
                else:
                    textboxText += event.unicode
                try:
                    xPos[selectedIndex] = int(textboxText)
                    announcementText = "Esc to deselect the point"
                except:
                    announcementText = "Input a number"
                generateTrajectory()
                if textboxText != str(xPos[selectedIndex]):
                    xPos[selectedIndex] = textboxText
                    drawAllTextboxes()
                    xPos[selectedIndex] = 0
                else:
                    drawAllTextboxes()
            elif appState == "edit yVelo":
                if event.key == pygame.K_RETURN:
                    appState = "selected point"
                elif event.key == pygame.K_BACKSPACE:
                    textboxText = textboxText[:-1]
                else:
                    textboxText += event.unicode
                try:
                    yVelo[selectedIndex] = int(textboxText)
                    announcementText = "Esc to deselect the point"
                except:
                    announcementText = "Input a number"
                generateTrajectory()
                if textboxText != str(yVelo[selectedIndex]):
                    yVelo[selectedIndex] = textboxText
                    drawAllTextboxes()
                    yVelo[selectedIndex] = 0
                else:
                    drawAllTextboxes()
            elif appState == "edit yPos":
                if event.key == pygame.K_RETURN:
                    appState = "selected point"
                elif event.key == pygame.K_BACKSPACE:
                    textboxText = textboxText[:-1]
                else:
                    textboxText += event.unicode
                try:
                    yPos[selectedIndex] = int(textboxText)
                    announcementText = "Esc to deselect the point"
                except:
                    announcementText = "Input a number"
                generateTrajectory()
                if textboxText != str(yPos[selectedIndex]):
                    yPos[selectedIndex] = textboxText
                    drawAllTextboxes()
                    yPos[selectedIndex] = 0
                else:
                    drawAllTextboxes()
            # Export
            if appState == "export":
                if event.key == pygame.K_RETURN:
                    fieldMod = 1
                    if startingSide == "red":
                        fieldMod = -1
                    xPos0 = xPos[0]
                    xVelo0 = xVelo[0]
                    yPos0 = yPos[0]
                    yVelo0 = yVelo[0]
                    for i in range(len(xPos)):
                        xPos[i] = round(interpolate(xPos[i],xPos0,pixel_per_inch),3) * fieldMod # actually y on the field
                        xVelo[i] = round(interpolate(xVelo[i],xVelo0,pixel_per_inch),3) * fieldMod
                        yPos[i] = round(interpolate(yPos[i],yPos0,pixel_per_inch),3) * -fieldMod # actually x on the field
                        yVelo[i] = round(interpolate(yVelo[i],yVelo0,pixel_per_inch),3) * -fieldMod
                        if startingSide == "red":
                            dir[i] -= 180
                    with open(file_path + textboxText + ".txt", "w") as file:
                        file.write("(x: "+str(yPos[0])+", y: "+str(xPos[0])+", x velo: "+str(yVelo[0])+", y velo: "+str(xVelo[0])+", direction: "+str(dir[0])+")")
                        for i in range(len(xPos)-1):
                            file.write("\n(x: "+str(yPos[i+1])+", y: "+str(xPos[i+1])+", x velo: "+str(yVelo[i+1])+", y velo: "+str(xVelo[i+1])+", time: "+str(tf[i])+", direction: "+str(dir[i+1])+")")
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    textboxText = textboxText[:-1]
                    generateTrajectory()
                    pygame.draw.rect(screen, Black, inputTextBox, 2)
                else:
                    textboxText += event.unicode
                screen.blit(textBoxTextFont.render(textboxText, False, Black),  (inputTextBox.x + 5, inputTextBox.y + 5))
                pygame.display.flip()
            # Sets the mode to adding new points
            elif event.key == pygame.K_q and appState == "edit points":
                appState = "new pos"
                announcementText = "Click and drag to create a new point"
                generateTrajectory()
            # Sets the mode to editing points
            elif (event.key == pygame.K_e and appState == "new pos") or (event.key == pygame.K_ESCAPE and appState == "selected point"):
                selectedIndex = -1
                appState = "edit points"
                announcementText = "Select a point to start editing"
                generateTrajectory() 
            # Simulates a robot running the trajectory
            elif event.key == pygame.K_w and (appState == "new pos" or appState == "edit points"):
                appState = "run trajectory"
                currentPose = 0
                currentTime = 0
                announcementText = "Running trajectory"
                screen.blit(textBoxTextFont.render(announcementText, False, Black), (announcementTextBox.x + 5, announcementTextBox.y + 5))
                pygame.display.flip()
            # Removes the selected point
            elif event.key == pygame.K_r and appState == "selected point":
                xPos.pop(selectedIndex)
                yPos.pop(selectedIndex)
                xVelo.pop(selectedIndex)
                yVelo.pop(selectedIndex)
                if selectedIndex > 0:
                    tf.pop(selectedIndex-1)
                elif len(tf) > 0:
                    tf.pop(0)
                generateTrajectory()
                selectedIndex = -1
                # Resets appState if the position list is empty
                if len(xPos) == 0:
                    appState = "start pos"
                    announcementText = "Choose a starting point"
                    generateTrajectory()
                else:
                    appState = "edit points"
            elif event.key == pygame.K_t and (appState == "new pos" or appState == "edit points"):
                appState = "export"
                generateTrajectory()
                pygame.draw.rect(screen, Black, inputTextBox, 2)
                pygame.display.flip()
                textboxText = ""

 # ____________________________________________________________________________________________________

        # Mouse Click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseClickX, mouseClickY = pygame.mouse.get_pos()
            # Adding the starting point
            if appState == "start pos":
                if mouseClickX > screenWidth/2:
                    startingSide = "red"
                    xPos.append(((screenWidth + fieldWidth)/2)-(robotLength/2))
                    dir.append(180)
                else:
                    startingSide = "blue"
                    xPos.append(((screenWidth - fieldWidth)/2)+(robotLength/2))
                    dir.append(0)
                xVelo.append(0)
                yPos.append(mouseClickY)
                yVelo.append(0)
                generateTrajectory()
                pygame.draw.circle(screen, (0, 0, 0), (xPos[0], yPos[0]), 5)
                pygame.display.update()
            # Adds the location of new points to the position lists
            elif appState == "new pos":
                if pygame.Rect.collidepoint(fieldRect, mouseClickX, mouseClickY):
                    xPos.append(mouseClickX)
                    yPos.append(mouseClickY)
                    pygame.draw.circle(screen, (0, 0, 0), (mouseClickX, mouseClickY), 5)
                    pygame.display.update()
                else:
                    error = True
            # In edit mode, checks if the mouse has clicked on any point
            elif appState == "edit points":
                counter = 0
                while selectedIndex == -1 and counter < len(xPos):
                    if xPos[counter] - 5 < mouseClickX < xPos[counter] + 5 and yPos[counter] - 5 < mouseClickY < yPos[counter] + 5:
                        # Sets selectedIndex to the point that the mouse clicked
                        selectedIndex = counter
                        appState = "selected point"
                        # Adds the textboxes for editing the point
                        drawAllTextboxes()
                        announcementText = "Esc to deselect the point"
                        pygame.draw.rect(screen, White, announcementTextBox)
                        screen.blit(textBoxTextFont.render(announcementText, False, Black), (announcementTextBox.x + 5, announcementTextBox.y + 5))
                        pygame.display.flip()
                    counter += 1
            # Ways to interact with the selected point
            elif appState == "selected point":
                # Starts dragging a point
                if xPos[selectedIndex] - 5 < mouseClickX < xPos[selectedIndex] + 5 and yPos[selectedIndex] - 5 < mouseClickY < yPos[selectedIndex] + 5:
                    appState = "moving point"
                # Editing points
                elif pygame.Rect.collidepoint(tfTextBox, (event.pos)):
                    appState = "edit tf"
                    textboxText = str(tf[selectedIndex-1])
                elif pygame.Rect.collidepoint(dirTextBox, (event.pos)):
                    appState = "edit dir"
                    textboxText = str(dir[selectedIndex])
                elif pygame.Rect.collidepoint(xVeloTextBox, (event.pos)):
                    appState = "edit xVelo"
                    textboxText = str(xVelo[selectedIndex])
                elif pygame.Rect.collidepoint(xPosTextBox, (event.pos)):
                    appState = "edit xPos"
                    textboxText = str(xPos[selectedIndex])
                elif pygame.Rect.collidepoint(yVeloTextBox, (event.pos)):
                    appState = "edit yVelo"
                    textboxText = str(xVelo[selectedIndex])
                elif pygame.Rect.collidepoint(yPosTextBox, (event.pos)):
                    appState = "edit yPos"
                    textboxText = str(yPos[selectedIndex])

 # ____________________________________________________________________________________________________

        # Mouse Release
        if event.type == pygame.MOUSEBUTTONUP:
            mouseReleaseX, mouseReleaseY = pygame.mouse.get_pos()
            # Swaps out of the start pos state after it's created
            if appState == "start pos":
                appState = "new pos"
                announcementText = "Click and drag to create a new point"
                generateTrajectory()
            # Adds the velocity of the new points to the velocity lists
            elif appState == "new pos" and not error:
                xVelo.append(mouseReleaseX - mouseClickX)
                yVelo.append(mouseReleaseY - mouseClickY)
                textboxText = ""
                appState = "set tf"
                pygame.draw.line(screen, Red, (mouseClickX,mouseClickY),(mouseReleaseX,mouseReleaseY))
                pygame.draw.rect(screen, Black, inputTextBox, 2)
                announcementText = "Input how much seconds to get to the point"
                pygame.draw.rect(screen, White, announcementTextBox)
                screen.blit(textBoxTextFont.render(announcementText, False, Black), (announcementTextBox.x + 5, announcementTextBox.y + 5))
                pygame.display.flip()
            # Stops dragging a point
            elif appState == "moving point":
                appState = "selected point"
                drawAllTextboxes()
            error = False

 # ____________________________________________________________________________________________________

        if event.type == pygame.MOUSEMOTION:
            # The actuall point dragging code
            if appState == "moving point":
                xPos[selectedIndex] = event.pos[0]
                yPos[selectedIndex] = event.pos[1]
                generateTrajectory()
                drawAllTextboxes()
            # Starting position robot image
            elif appState == "start pos":
                generateTrajectory()
                if event.pos[0] > screenWidth/2:
                    robot = Rect(((screenWidth + fieldWidth)/2)-robotLength, event.pos[1]-(robotWidth/2), robotLength, robotWidth)
                    pygame.draw.rect(screen,(100,100,100),robot)
                else:
                    robot = Rect((screenWidth - fieldWidth)/2, event.pos[1]-(robotWidth/2), robotLength, robotWidth)
                    pygame.draw.rect(screen,(100,100,100),robot)
                pygame.display.flip()
        # Exit
        if event.type == pygame.QUIT:
            running=0

 # ____________________________________________________________________________________________________

    # Simulating the robot running the Trajectory
    if appState == "run trajectory":
        if currentPose < len(tf):
            # Setting up variables
            x0 = xPos[currentPose]
            xf = xPos[currentPose + 1]
            xV0 = xVelo[currentPose]
            xVf = xVelo[currentPose + 1]

            y0 = yPos[currentPose]
            yf = yPos[currentPose + 1]
            yV0 = yVelo[currentPose]
            yVf = yVelo[currentPose + 1]

            # Trajectory Generation Setup again

            xA = x0
            xB = xV0
            xC = ((3 * (xf - x0))/(tf[currentPose]**2)) - (((2 * xV0) + xVf)/tf[currentPose])
            xD = -1*((2 * (xf - x0))/(tf[currentPose]**3)) + ((xV0 + xVf)/(tf[currentPose]**2))

            yA = y0
            yB = yV0
            yC = ((3 * (yf - y0))/(tf[currentPose]**2)) - (((2 * yV0) + yVf)/tf[currentPose])
            yD = -1*((2 * (yf - y0))/(tf[currentPose]**3)) + ((yV0 + yVf)/(tf[currentPose]**2))

            if currentTime <= tf[currentPose]:
                # Drawing the robot
                xP = xA + (xB * currentTime) + (xC * (currentTime**2)) + (xD * (currentTime**3))
                yP = yA + (yB * currentTime) + (yC * (currentTime**2)) + (yD * (currentTime**3))
                currentTime += 0.001 * deltaTime
                generateTrajectory()
                cDir = dir[currentPose] + ((dir[currentPose + 1] - dir[currentPose])*currentTime/tf[currentPose])
                robot = Rect(xP - (robotLength/2), yP - (robotWidth/2), robotLength, robotWidth)
                pygame.draw.rect(screen,(100,100,100),robot)
                pygame.draw.line(screen, Green, (xP,yP),(xP+(math.cos(math.radians(cDir))*50),yP+(math.sin(math.radians(cDir))*50)),4)
                pygame.display.update()
            else:
                currentTime = 0
                currentPose += 1
        else:
            appState = "new pos"
            announcementText = "Click and drag to create a new point"
            generateTrajectory()

 # ____________________________________________________________________________________________________

    deltaTime = pygame.time.get_ticks() - time
    time = pygame.time.get_ticks()
    clock.tick(40) 
pygame.quit()