import pygame
from screens.screen_manager import ScreenManager
from screens.title_screen import TitleScreen
from screens.tutorial_screen import TutorialScreen
from screens.settings_screen import SettingsScreen
from screens.main_menu_screen import MainMenuScreen
from screens.game_play_screen import GamePlayScreen

from core.progress_manager import ProgressManager
from core.game_manager import GameManager

pygame.init()

try:
    import config
    screen_width = config.SCREEN_WIDTH
    screen_height = config.SCREEN_HEIGHT
    fps = config.FPS
except (ImportError, AttributeError):
    print("Warning: config.py not found or incomplete. Using default values.")
    screen_width = 800
    screen_height = 600
    fps = 60

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("apt-get packages")
clock = pygame.time.Clock()

# inits innit
progress_manager = ProgressManager()
game_manager = GameManager(progress_manager) 
screen_manager = ScreenManager()

# Screens Shenanigans
title_screen = TitleScreen()
tutorial_screen = TutorialScreen()
settings_screen = SettingsScreen(game_manager_ref=game_manager)
main_menu_screen = MainMenuScreen(game_manager=game_manager) 
game_play_screen = GamePlayScreen()

screen_manager.add_screen('title', title_screen)
screen_manager.add_screen('tutorial', tutorial_screen)
screen_manager.add_screen('settings', settings_screen)
screen_manager.add_screen('main_menu', main_menu_screen)
screen_manager.add_screen('game_play', game_play_screen)

screen_manager.go_to_screen('title')

# Main loop
running = True
while running:
    dt = clock.tick(fps) / 1000.0  # Delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        screen_manager.handle_event(event) # ScreenManager handles event distribution

    screen_manager.update(dt)
    screen_manager.render(screen) # Render current screen        

    pygame.display.flip()

pygame.quit()