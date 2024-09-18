# WPIWITDH Beta 0.7
# Version Notes: Changeed trajectory generation technique

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
screen.fill((225,225,225))

field = pygame.image.load("Images/FTC-field.png")
field = pygame.transform.scale(field, (fieldWidth, fieldHeight))
fieldRect = Rect((screenWidth - fieldWidth)/2, (screenHeight - fieldHeight)/2, fieldWidth, fieldHeight)

screen.blit(field, ((screenWidth - fieldWidth)/2, (screenHeight - fieldHeight)/2))
pygame.display.update()

# Textboxes

announcementTextBox = Rect(0,10,screenWidth,50)

inputTextBox = Rect((screenWidth/2)-screenWidth/4,screenHeight-60,screenWidth/2,50)

dirTextBox = Rect(screenWidth-(screenWidth/4)+50-20-screenWidth*0.25,screenHeight-60,(screenWidth/4)-50,50)
xVeloTextBox = Rect(20,screenHeight-60,(screenWidth/4)-50,50)
xPosTextBox = Rect(20,screenHeight-150,(screenWidth/4)-50,50)
yVeloTextBox = Rect(screenWidth-(screenWidth/4)+50-20,screenHeight-60,(screenWidth/4)-50,50)
yPosTextBox = Rect(screenWidth-(screenWidth/4)+50-20,screenHeight-150,(screenWidth/4)-50,50)

# Trajectory Variables

xPos = [] # x position
xVelo = [] # x velocity at the point

yPos = [] # y position
yVelo = [] # y velocity at the point

dir = [] # direction at the point

startingSide = ""

currentPose = 0
currentTime = 0

 # ________________________________________________________________________________________________________________________________________________________________________________________________________

def generateTrajectory():
    screen.fill((225,225,225))
    screen.blit(field, ((screenWidth - fieldWidth)/2, (screenHeight - fieldHeight)/2))

    cPose = 0
    # Drawing the starting point
    if len(xPos) > 0:
        pygame.draw.line(screen, Green, (xPos[0],yPos[0]),(xPos[0]+(math.cos(math.radians(dir[0]))*50),yPos[0]+(math.sin(math.radians(dir[0]))*50)))
        pygame.draw.circle(screen, (0, 0, 0), (xPos[0], yPos[0]), 5)
    while cPose < len(xPos)-1:
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
        t = 0
        while t <= 1:
            A = (2*(t**3))-(3*(t**2))+1
            B = (-2*(t**3))+(3*(t**2))
            C = (t**3)-(2*(t**2))+t
            D = (t**3)-(t**2)
            # Cubic Trajectory Generation 
            xP = (x0*A) + (xf*B) + (xV0*C) + (xVf*D)
            yP = (y0*A) + (yf*B) + (yV0*C) + (yVf*D)
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

 # ________________________________________________________________________________________________________________________________________________________________________________________________________

def drawTextbox(textbox, text):
    pygame.draw.rect(screen, Black, textbox, 2)
    screen.blit(textBoxTextFont.render(str(text), False, Black),  (textbox.x + 5, textbox.y + 5))
    pygame.display.flip()    

def drawAllTextboxes():
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

def convertToPoint(angle, xPosition, yPosition):
    pointLength = ((robotLength/2)/(math.cos(math.atan(robotWidth/robotLength))))
    return ((math.cos(angle) * pointLength) + xPosition,(math.sin(angle) * pointLength) + yPosition)

 # ________________________________________________________________________________________________________________________________________________________________________________________________________

def exportText(file, fileName):
    # file.write("(x: "+str(yPos[0])+", y: "+str(xPos[0])+", x velo: "+str(yVelo[0])+", y velo: "+str(xVelo[0])+", direction: "+str(dir[0])+")")
    # for i in range(len(xPos)-1):
    #     file.write("\n(x: "+str(yPos[i+1])+", y: "+str(xPos[i+1])+", x velo: "+str(yVelo[i+1])+", y velo: "+str(xVelo[i+1])+", direction: "+str(dir[i+1])+")")
    file.write('''
@Autonomous
public class ''' + fileName + ''' extends CommandOpMode {
    public static double xkP = 7;
    public static double xkI = 0.015;
    public static double xkD = 0.04;

    public static double ykP = 7;
    public static double ykI = 0.015;
    public static double ykD = 0.05;

    public static double tkP = 3;
    public static double tkI = 1.0;
    public static double tkD = 0.001;

    public static int VEL = 30;
    public static int ACCEL = 30;
    public static double RUNTIME_TOLERANCE_PCT = .7;

    private final TrajectoryConfig trajectoryConfig = new TrajectoryConfig(VEL, ACCEL);

    @Override
    public void initialize() {
               
        ChasarsisSubsystem chassisSubsystem = new ChassisSubsystem(hardwareMap);
        CameraSubsystem cameraSubsystem   = new CameraSubsystem(hardwareMap);
        BlinkinSubsystem blinkinSubsystem = new BlinkinSubsystem(hardwareMap);
        SpatulaSubsystem spatulaSubsystem = new SpatulaSubsystem(hardwareMap);
        SlideSubsystem slideSubsystem     = new SlideSubsystem(hardwareMap);

        // Setup trajectories

        HolonomicDriveController controller = new HolonomicDriveController(
                new Pose2d(1, 1, Rotation2d.fromDegrees(3)),
                new PIDController(xkP, xkI, xkD),
                new PIDController(ykP, ykI, ykD),
                new ProfiledPIDController(
                        tkP, tkI, tkD, new TrapezoidProfile.Constraints(10000, 10000)
                )
        );

        ArrayList<TrajectoryConfig> trajectoryConfigs = new ArrayList<>(Arrays.asList(
        	new TrajectoryConfig(VEL, ACCEL)''')
    for i in range(len(xPos)-2):
	    file.write(''',
        	new TrajectoryConfig(VEL, ACCEL)''')
    file.write('''
	    ))''')
    for i in range(len(xPos)-1):
	    file.write('''
        trajectoryConfig.get('''+str(i)+''').setStartVelocity('''+str(((xVelo[i]**2)+(yVelo[i]**2))**0.5)+''');
        trajectoryConfig.get('''+str(i)+''').setEndVelocity('''+str(((xVelo[i+1]**2)+(yVelo[i+1]**2))**0.5)+''');
	''')
    file.write('''
        ArrayList<Pair<Trajectory, Rotation2d>> trajectorySequence = TrajectorySequence.weaveTrajectorySequence(''')
    for i in range(len(xPos)-1):
        dir0 = 0 
        dirF = 0
        if yVelo[i] != 0:
            dir0 = math.atan(xVelo[i]/yVelo[i])
        if yVelo[i+1] != 0:
            dirF = math.atan(xVelo[i+1]/yVelo[i+1])
        
        file.write('''
            new TrajectorySegment(
                Rotation2d.fromDegrees('''+str(math.degrees(dir0))+'''),
                new Translation2d[0],
                new Pose2d('''+str(xPos[i+1])+", "+str(yPos[i+1])+", Rotation2d.fromDegrees("+str(math.degrees(dirF))+''')),
                Rotation2d.fromDegrees('''+str(dir[i+1])+'''),
                trajectoryConfig.get('''+str(i)+''')
            )''')
        if (i != len(xPos) - 2):
            file.write(",")
    file.write('''
        )
        CommandScheduler.getInstance().schedule(''')
    for i in range(len(xPos)-1):
        file.write('''
            new FollowTrajectory(
                chassisSubsystem, controller, trajectorySequence.get('''+str(i)+''') ,RUNTIME_TOLERANCE_PCT
            )''')
        if (i != len(xPos) - 2):
            file.write(",")
    file.write('''
        );
    }
}''')
    

screen.blit(textBoxTextFont.render(announcementText, False, Black), (announcementTextBox.x + 5, announcementTextBox.y + 5))
screen.blit(instructionTextFont.render("Q to create new points", False, Black), (5, 60))
screen.blit(instructionTextFont.render("W to run the trajectory", False, Black), (5, 75))
screen.blit(instructionTextFont.render("E to edit points", False, Black), (5, 90))
screen.blit(instructionTextFont.render("R to delete selected points", False, Black), (5, 105))
screen.blit(instructionTextFont.render("T to finish and save trajectory", False, Black), (5, 120))
pygame.display.flip()

 # ________________________________________________________________________________________________________________________________________________________________________________________________________

while running:
    for event in pygame.event.get():
        # Key press
        if event.type == pygame.KEYDOWN:
            # Input textboxes
            if appState == "set dir":
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

 # ________________________________________________________________________________________________________________________________________________________________________________________________________

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
                        xPos[i] = round(interpolate(xPos[i],xPos0,pixel_per_inch),3) # actually y on the field
                        xVelo[i] = round(interpolate(xVelo[i],xVelo0,pixel_per_inch),3)
                        yPos[i] = round(interpolate(yPos[i],yPos0,pixel_per_inch),3) # actually x on the field
                        yVelo[i] = round(interpolate(yVelo[i],yVelo0,pixel_per_inch),3)
                        if startingSide == "red":
                            dir[i] -= 180
                    with open(file_path + textboxText + ".txt", "w") as file:
                        exportText(file, textboxText)
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    textboxText = textboxText[:-1]
                    generateTrajectory()
                    pygame.draw.rect(screen, Black, inputTextBox, 2)
                else:
                    textboxText += event.unicode
                screen.blit(textBoxTextFont.render(textboxText, False, Black),  (inputTextBox.x + 5, inputTextBox.y + 5))
                pygame.display.flip()
                
 # ________________________________________________________________________________________________________________________________________________________________________________________________________

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

 # ________________________________________________________________________________________________________________________________________________________________________________________________________

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

 # ________________________________________________________________________________________________________________________________________________________________________________________________________

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
                textboxText = str(dir[len(dir)-1])
                appState = "set dir"
                pygame.draw.line(screen, Red, (mouseClickX,mouseClickY),(mouseReleaseX,mouseReleaseY))
                drawTextbox(inputTextBox, textboxText)
                announcementText = "Input the heading of the robot"
                pygame.draw.rect(screen, (230,230,230), announcementTextBox)
                screen.blit(textBoxTextFont.render(announcementText, False, Black), (announcementTextBox.x + 5, announcementTextBox.y + 5))
                pygame.display.flip()
            # Stops dragging a point
            elif appState == "moving point":
                appState = "selected point"
                drawAllTextboxes()
            error = False

 # ________________________________________________________________________________________________________________________________________________________________________________________________________

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

 # ________________________________________________________________________________________________________________________________________________________________________________________________________

    # Simulating the robot running the Trajectory
    if appState == "run trajectory":
        if currentPose < len(xPos)-1:
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

            if currentTime <= 1:
                # Drawing the robot
                A = 2*(currentTime**3)-3*(currentTime**2)+1
                B = -2*(currentTime**3)+3*(currentTime**2)
                C = (currentTime**3)-2*(currentTime**2)+currentTime
                D = (currentTime**3)-(currentTime**2)
            # Cubic Trajectory Generation 
                xP = (x0*A) + (xf*B) + (xV0*C) + (xVf*D)
                yP = (y0*A) + (yf*B) + (yV0*C) + (yVf*D)
                currentTime += 0.001 * deltaTime
                generateTrajectory()
                cDir = dir[currentPose] + ((dir[currentPose + 1] - dir[currentPose])*currentTime)
                topLeft = math.radians(cDir - 180) + math.atan(robotWidth/robotLength)
                topRight = math.radians(cDir) - math.atan(robotWidth/robotLength)
                bottomLeft = math.radians(cDir + 180) - math.atan(robotWidth/robotLength)
                bottomRight = math.radians(cDir) + math.atan(robotWidth/robotLength)
                pygame.draw.polygon(screen,(100,100,100),[convertToPoint(topLeft,xP,yP),convertToPoint(topRight,xP,yP),convertToPoint(bottomRight,xP,yP),convertToPoint(bottomLeft,xP,yP)])
                pygame.draw.line(screen, Green, (xP,yP),(xP+(math.cos(math.radians(cDir))*robotLength/2),yP+(math.sin(math.radians(cDir))*robotLength/2)),4)
                pygame.display.update()
            else:
                currentTime = 0
                currentPose += 1
        else:
            appState = "new pos"
            announcementText = "Click and drag to create a new point"
            generateTrajectory()

 # ________________________________________________________________________________________________________________________________________________________________________________________________________

    deltaTime = pygame.time.get_ticks() - time
    time = pygame.time.get_ticks()
    clock.tick(40) 
pygame.quit()
