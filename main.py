import pygame
import functions_extras

screen  = pygame.display.set_mode((1280, 720))
screen.fill("purple")
pygame.display.set_caption("1869AC")
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    functions_extras.button(screen, 100, 40, 440, 440)
    functions_extras.button(screen, 100, 40, 300, 300)
    pygame.display.flip()

pygame.quit()
