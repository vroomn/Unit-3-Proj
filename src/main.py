import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
deltaTime = 0

run = True
while run:
    # Checks to see if the "x" button on the window has been pressed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                run = False
    
    deltaTime = clock.tick()

pygame.quit()