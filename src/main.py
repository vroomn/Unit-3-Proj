import pygame
import pygame.gfxdraw
import random

import dearpygui.dearpygui as dpg

import queue
import threading

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
deltaTime = 0.0

# __________________________________ Allows for a window to dynamically config the properties
#TODO: Combine callbacks with the pipe control dict
#def spacingCallback(sender, app_data):
#    pipeSpacing = app_data

#def ySpacingCallback(sender, app_data):
#    for i in pipes:
#        i.changePipeSpacing(app_data)

"""Multiple callback function that mutate the state of the pipes"""

def scrollSpeedCallback(sender, app_data):
    for i in pipes:
        i.scrollRate = app_data

def pipeReset(sender, app_data):
    for i in pipes:
        i.reset()

def yMinCallback(sender, app_data):
    for i in pipes:
        i.yAxisMin = app_data

def yMaxcallback(sender, app_data):
    for i in pipes:
        i.yAxisMax = app_data

def spacingMinCallback(sender, app_data):
    for i in pipes:
        i.pipeSpacingMin = app_data

def spacingMaxCallback(sender, app_data):
    for i in pipes:
        i.pipeSpacingMax = app_data

def gravityChangeCallback(sender, app_data):
    flappy.gravityWeight = app_data

def setMaxVelocityCallback(sender, app_data):
    flappy.velocityMax = app_data

def setJumpStrengthCallback(sender, app_data):
    jumpStrength = app_data

pipeControlIds = queue.Queue(3)

# Function to hold the logic that will be on a seperate thread
def dpgManagement():
    dpg.create_context()
    dpg.create_viewport(title="Config Menu", width=600, height=300)

    with dpg.window(label="Pipe Configuration"):
        dpg.add_text("Active Pipe Config")
        #pipeControlIds.put(dpg.add_slider_int(label="Pipe Spacing", min_value=100, default_value=120, max_value=400, callback=spacingCallback)) TODO: Add individual adjustments to height and y spacing
        #pipeControlIds.put(dpg.add_slider_int(label="Pipe Y Offset", default_value=200, min_value=0, max_value=300, callback=ySpacingCallback))
        pipeControlIds.put(dpg.add_slider_int(label="Pipe Scroll Speed", default_value=102, min_value=60, max_value=1000, callback=scrollSpeedCallback))
        dpg.add_button(label="Reset Tube Pos", callback=pipeReset)

        dpg.add_text("Reset Parameters")
        dpg.add_input_int(label="Y Axis Minimum", default_value=150, callback=yMinCallback)
        dpg.add_input_int(label="Y Axis Minimum", default_value=screen.get_height()-150, callback=yMaxcallback)
        dpg.add_input_int(label="Spacing Minimum", default_value=200, callback=spacingMinCallback)
        dpg.add_input_int(label="Spacing Maximum", default_value=300, callback=spacingMaxCallback)

    with dpg.window(label="Bird Settings"):
        dpg.add_slider_float(label="Gravity Weighting", default_value=5, min_value=0, max_value=50, callback=gravityChangeCallback)
        dpg.add_slider_float(label="Velocity Max", default_value=10, min_value=0, max_value=100, callback=setMaxVelocityCallback)
        dpg.add_slider_float(label="Jump Strength", default_value=10, min_value=0, max_value=100, callback=setJumpStrengthCallback)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

dpgThread = threading.Thread(target=dpgManagement, args=())
dpgThread.start()

pipeControls = {#"Pipe Spacing": pipeControlIds.get(),
                #"Pipe Y Offset": pipeControlIds.get(),
                "Pipe Scroll Speed": pipeControlIds.get()}

# __________________________________

class GameObject:
    def __init__(self, width, height, xPos, yPos) -> None:
        self.rect = pygame.Rect(xPos, yPos, width, height)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha() #Enables transparency

    # Render the wireframe of the object's rect
    def wireframeDraw(self, color: (int, int, int)) -> None:
        pygame.gfxdraw.rectangle(screen, self.rect, color) # Draws white rectangle for wireframe

    # Update the position or height of an object
    def update(self, width, height, xPos, yPos) -> None:
        if height < 1:
            height = 1
        self.surface = pygame.transform.scale(self.surface, (width, height))
        self.rect.update(xPos, yPos, width, height)

    # Move the object by a certian value
    def move(self, x, y):
        self.rect = self.rect.move(x, y)

# An object that holds all the relevent data for a pipe and mutation of it's state
class PipeStack():
    def __init__(self, xOffset: int, idx: int) -> None:
        self.index = idx
        self.initX = screen.get_width()
        self.ySpacing = 200
        self.scrollRate = 102
        self.yAxisMin = 150
        self.yAxisMax = screen.get_height()-150
        self.pipeSpacingMin = 200
        self.pipeSpacingMax = 300
        self.originY = random.randrange(self.yAxisMin, self.yAxisMax)

        self.topEntry = GameObject(100, 50, self.initX+xOffset, self.originY-150)
        self.topTube = GameObject(88, self.originY-150, self.initX+6+xOffset, 0)

        self.bottomEntry = GameObject(100, 50, self.initX+xOffset, self.originY+100)
        self.bottomTube = GameObject(88, screen.get_height()-(self.originY+100), self.initX+6+xOffset, self.originY+150)

        self.rects = [self.topTube.rect, self.topEntry.rect, self.bottomEntry.rect, self.bottomTube.rect]
    
    
    # Change the spacing between the top and bottom of the tube sections
    def changePipeSpacing(self, dist) -> None:
        self.ySpacing = dist
        dist = dist/2
        topRect = self.topEntry.rect
        topRect.update(topRect.x, (self.originY-50)-dist, topRect.width, topRect.height)
        self.topTube.update(self.topTube.rect.width, (self.originY-50)-dist, self.topTube.rect.x, self.topTube.rect.y)

        botRect = self.bottomEntry.rect
        botRect.update(botRect.x, self.originY+dist, botRect.width, botRect.height)
        self.bottomTube.update(self.bottomTube.rect.width, screen.get_height()-(self.originY+dist), self.bottomTube.rect.x, self.originY+dist+50)
    
    # Shift the pipe left by the scroll rate
    def scroll(self):
        scrollRate = -self.scrollRate*deltaTime
        self.topEntry.move(scrollRate, 0)
        self.topTube.move(scrollRate, 0)

        self.bottomEntry.move(scrollRate, 0)
        self.bottomTube.move(scrollRate, 0)
        pipes[self.index].rects = [self.topTube.rect, self.topEntry.rect, self.bottomEntry.rect, self.bottomTube.rect]

    # Move the pipe over to a new location offscreen
    def reset(self):
        #TODO: Compress into function that can perfom the same task, add all to array
        self.topEntry.move((self.initX-self.topEntry.rect.x), 0)
        self.topTube.move(((self.initX-self.topTube.rect.x)+6), 0)
        self.bottomEntry.move((self.initX-self.bottomEntry.rect.x), 0)
        self.bottomTube.move(((self.initX-self.bottomTube.rect.x)+6), 0)

        # Adjust the spacing and the Y axis alignment
        self.originY = random.randrange(self.yAxisMin, self.yAxisMax)
        self.changePipeSpacing(random.randrange(self.pipeSpacingMin, self.pipeSpacingMax))

        # Pipe new values into the dev panel
        #dpg.set_value(pipeControls["Pipe Y Offset"], self.ySpacing)
        #dpg.set_value(pipeControls["Pipe Y Offset"])

    # Draw all the wireframes for the gameobjects
    def wireframeDraw(self) -> None:
        self.bottomEntry.wireframeDraw((207, 93, 85))
        self.bottomTube.wireframeDraw((207, 93, 85))

        self.topEntry.wireframeDraw((207, 93, 85))
        self.topTube.wireframeDraw((207, 93, 85))

def gameOver():
    run = False

#FIXME: Spacing of the pipe and setup need overhaul for consistent output
pipeSpacing = 200

numOfPipes = round(screen.get_width()/(pipeSpacing+100))
pipes = []

for i in range(numOfPipes):
    pipes.append(PipeStack((pipeSpacing+100)*i, i))

class Flappy(GameObject):
    def __init__(self, width, height, xPos, yPos) -> None:
        super().__init__(width, height, xPos, yPos)
        self.yVelocity:float = 0
        self.gravityWeight:float = 5
        self.velocityMax:float = 10

    def physicsUpdate(self):
        self.yVelocity += (self.gravityWeight*deltaTime)
        if self.yVelocity > self.velocityMax:
            self.yVelocity = self.velocityMax
        self.move(0, self.yVelocity)
    
    def wireframeDraw(self) -> None:
        return super().wireframeDraw((255, 255, 255))
    
    def collisionCheck(self):
        if self.rect.y <= 0 or self.rect.y >= 720:
            global run
            run = False

        for pipe in pipes:
            for rect in pipe.rects:
                if (
                    self.rect.x + self.rect.width > rect.x and
                    self.rect.x < rect.x + rect.width and 
                    self.rect.y + self.rect.height > rect.y and 
                    self.rect.y < rect.y + rect.width
                ):
                    run = False


flappy = Flappy(60, 40, 100, screen.get_height()/2)
jumpStrength = 10

run = True
while run:
    screen.fill((0, 0, 0))
    # Checks to see if the "x" button on the window has been pressed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                run = False
        elif event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                flappy.yVelocity -= jumpStrength

    # Rendering and moving around the pipes
    for i in pipes:
        i.wireframeDraw()
        i.scroll()
        if i.bottomEntry.rect.x+i.bottomEntry.rect.width <= 0:
            i.reset()

    # Flappy characher render
    flappy.wireframeDraw()
    flappy.physicsUpdate()
    flappy.collisionCheck()

    pygame.display.flip()
    deltaTime = clock.tick(60)/1000

dpgThread.join()
pygame.quit()