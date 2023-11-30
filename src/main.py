import pygame
import pygame.gfxdraw
import random

import dearpygui.dearpygui as dpg

import queue
import threading


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
deltaTime = 0.0

# __________________________________ Allows for a window to dynamically config the properties
#TODO: Combine callbacks with the pipe control dict
def spacingCallback(sender, app_data):
    pipeOne.changePipeSpacing(app_data)

def yOffsetCallback(sender, app_data):
    pipeOne.originY = app_data
    pipeOne.changePipeSpacing(pipeOne.spacing)

def scrollSpeedCallback(sender, app_data):
    pipeOne.scrollRate = app_data

def pipeReset(sender, app_data):
    pipeOne.reset()

def yMinCallback(sender, app_data):
    pipeOne.yAxisMin = app_data

def yMaxcallback(sender, app_data):
    pipeOne.yAxisMax = app_data

def spacingMinCallback(sender, app_data):
    pipeOne.pipeSpacingMin = app_data

def spacingMaxCallback(sender, app_data):
    pipeOne.pipeSpacingMax = app_data

pipeControlIds = queue.Queue(3)

def dpgManagement():
    dpg.create_context()
    dpg.create_viewport(title="Config Menu", width=600, height=300)

    with dpg.window(label="Pipe Configuration"):
        dpg.add_text("Active Pipe Config")
        pipeControlIds.put(dpg.add_slider_int(label="Pipe Spacing", default_value=200, min_value=0, max_value=300, callback=spacingCallback))
        pipeControlIds.put(dpg.add_slider_int(label="Pipe Y Pos", default_value=screen.get_height()/2, min_value=150, max_value=screen.get_height()-150, callback=yOffsetCallback))
        pipeControlIds.put(dpg.add_slider_int(label="Pipe Scroll Speed", default_value=102, min_value=60, max_value=500, callback=scrollSpeedCallback))
        dpg.add_button(label="Reset Tube Pos", callback=pipeReset)
        dpg.add_text("Reset Parameters")
        dpg.add_input_int(label="Y Axis Minimum", default_value=150, callback=yMinCallback)
        dpg.add_input_int(label="Y Axis Minimum", default_value=screen.get_height()-150, callback=yMaxcallback)
        dpg.add_input_int(label="Spacing Minimum", default_value=200, callback=spacingMinCallback)
        dpg.add_input_int(label="Spacing Maximum", default_value=300, callback=spacingMaxCallback)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

dpgThread = threading.Thread(target=dpgManagement, args=())
dpgThread.start()

pipeControls = {"Pipe Spacing": pipeControlIds.get(),
                "Pipe Y Pos": pipeControlIds.get(),
                "Pipe Scroll Speed": pipeControlIds.get()}

# __________________________________

class GameObject:
    def __init__(self, width, height, xPos, yPos) -> None:
        self.rect = pygame.Rect(xPos, yPos, width, height)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha() #Enables transparency

    def wireframeDraw(self) -> None:
        pygame.gfxdraw.rectangle(screen, self.rect, (255, 255, 255)) # Draws white rectangle for wireframe

    def update(self, width, height, xPos, yPos) -> None:
        self.surface = pygame.transform.scale(self.surface, (width, height))
        self.rect.update(xPos, yPos, width, height)

    def move(self, x, y):
        self.rect = self.rect.move(x, y)

class PipeStack():
    def __init__(self) -> None:
        initX = screen.get_width()
        self.spacing = 200
        self.scrollRate = 102
        self.yAxisMin = 150
        self.yAxisMax = screen.get_height()-150
        self.pipeSpacingMin = 200
        self.pipeSpacingMax = 300
        self.originY = random.randrange(self.yAxisMin, self.yAxisMax)

        self.topEntry = GameObject(100, 50, initX, self.originY-150)
        self.topTube = GameObject(88, self.originY-150, initX+6, 0)

        self.bottomEntry = GameObject(100, 50, initX, self.originY+100)
        self.bottomTube = GameObject(88, screen.get_height()-(self.originY+100), initX+6, self.originY+150)
    
    def changePipeSpacing(self, dist) -> None:
        self.spacing = dist
        dist = dist/2
        topRect = self.topEntry.rect
        topRect.update(topRect.x, (self.originY-50)-dist, topRect.width, topRect.height)
        self.topTube.update(self.topTube.rect.width, (self.originY-50)-dist, self.topTube.rect.x, self.topTube.rect.y)

        botRect = self.bottomEntry.rect
        botRect.update(botRect.x, self.originY+dist, botRect.width, botRect.height)
        self.bottomTube.update(self.bottomTube.rect.width, screen.get_height()-(self.originY+dist), self.bottomTube.rect.x, self.originY+dist+50)
    
    def scroll(self):
        scrollRate = -self.scrollRate*deltaTime
        self.topEntry.move(scrollRate, 0)
        self.topTube.move(scrollRate, 0)

        self.bottomEntry.move(scrollRate, 0)
        self.bottomTube.move(scrollRate, 0)

    def reset(self):
        #TODO: Compress into function that can perfom the same task, add all to array
        resetPos = screen.get_width()
        self.topEntry.move(resetPos-self.topEntry.rect.x, 0)
        self.topTube.move((resetPos-self.topTube.rect.x)+6, 0)
        self.bottomEntry.move(resetPos-self.bottomEntry.rect.x, 0)
        self.bottomTube.move((resetPos-self.bottomTube.rect.x)+6, 0)

        # Adjust the spacing and the Y axis alignment
        self.originY = random.randrange(self.yAxisMin, self.yAxisMax)
        self.changePipeSpacing(random.randrange(self.pipeSpacingMin, self.pipeSpacingMax))

        # Pipe new values into the dev panel
        dpg.set_value(pipeControls["Pipe Spacing"], self.spacing)
        dpg.set_value(pipeControls["Pipe Y Pos"], self.originY)


    def wireframeDraw(self) -> None:
        self.bottomEntry.wireframeDraw()
        self.bottomTube.wireframeDraw()

        self.topEntry.wireframeDraw()
        self.topTube.wireframeDraw()

pipeOne = PipeStack()

run = True
while run:
    screen.fill((0, 0, 0))
    # Checks to see if the "x" button on the window has been pressed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                run = False

    pipeOne.wireframeDraw()
    pipeOne.scroll()

    pygame.display.flip()
    deltaTime = clock.tick(60)/1000

dpgThread.join()
pygame.quit()