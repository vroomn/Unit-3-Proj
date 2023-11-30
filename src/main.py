import pygame
import pygame.gfxdraw
import random

import dearpygui.dearpygui as dpg

import threading


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
deltaTime = 0

class GameObject:
    def __init__(self, width, height, xPos, yPos) -> None:
        self.rect = pygame.Rect(xPos, yPos, width, height)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha() #Enables transparency

    def wireframeDraw(self) -> None:
        pygame.gfxdraw.rectangle(screen, self.rect, (255, 255, 255)) # Draws white rectangle for wireframe

    def update(self, width, height, xPos, yPos) -> None:
        self.surface = pygame.transform.scale(self.surface, (width, height))
        self.rect.update(xPos, yPos, width, height)

class PipeStack():
    def __init__(self) -> None:
        widthHalf = screen.get_width()/2
        self.initY = screen.get_height()/2

        self.topEntry = GameObject(100, 50, widthHalf, self.initY-150)
        self.topTube = GameObject(88, self.initY-150, widthHalf+6, 0)

        self.bottomEntry = GameObject(100, 50, widthHalf, self.initY+100)
        self.bottomTube = GameObject(88, screen.get_height()-(self.initY+100), widthHalf+6, self.initY+150)
    
    def changePipeSpacing(self, dist) -> None:
        dist = dist/2
        topRect = self.topEntry.rect
        topRect.update(topRect.x, (self.initY-50)-dist, topRect.width, topRect.height)
        self.topTube.update(self.topTube.rect.width, (self.initY-50)-dist, self.topTube.rect.x, self.topTube.rect.y)

        botRect = self.bottomEntry.rect
        botRect.update(botRect.x, self.initY+dist, botRect.width, botRect.height)
        self.bottomTube.update(self.bottomTube.rect.width, screen.get_height()-(self.initY+dist), self.bottomTube.rect.x, self.initY+dist+50)
    
    def wireframeDraw(self) -> None:
        self.bottomEntry.wireframeDraw()
        self.bottomTube.wireframeDraw()

        self.topEntry.wireframeDraw()
        self.topTube.wireframeDraw()

pipeOne = PipeStack()

# __________________________________ Allows for a window to dynamically config the properties
def spacingCallback(sender, app_data):
    pipeOne.changePipeSpacing(app_data)

def dpgManagement():
    dpg.create_context()
    dpg.create_viewport(title="Config Menu", width=600, height=300)

    with dpg.window(label="Pipe Configuration"):
        dpg.add_slider_int(label="Pipe Spacing", default_value=200, min_value=0, max_value=300, callback=spacingCallback)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

dpgThread = threading.Thread(target=dpgManagement, args=())
dpgThread.start()
# __________________________________

run = True
while run:
    screen.fill((0, 0, 0))
    # Checks to see if the "x" button on the window has been pressed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                run = False

    pipeOne.wireframeDraw()

    pygame.display.flip()
    deltaTime = clock.tick()

dpgThread.join()
pygame.quit()