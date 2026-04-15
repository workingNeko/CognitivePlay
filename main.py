import pygame
from screens.main_menu import MainMenu

pygame.init()

# Fullscreen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("SmartPlay Kinder")

clock = pygame.time.Clock()
menu = MainMenu(screen)
pygame.mixer.init()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        menu.handle_event(event)

    menu.update()
    menu.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
