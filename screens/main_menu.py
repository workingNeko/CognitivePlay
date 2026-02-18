# screens/main_menu.py
import pygame
from ui.button import Button
import os
from screens.mazegame import MazeGame
from screens.catchgame import CatchGame
from screens.stageselect import StageSelect
from screens.hiddenobject import HiddenObjectGame
from screens.minipuzzle import MiniPuzzleGame
from screens.knowledgegame import KnowledgeGame  # Add this import


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.w, self.h = screen.get_size()

        # --- Load background image ---
        bg_path = os.path.join("assets", "images", "menu_background.png")
        if os.path.exists(bg_path):
            self.bg_image = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (self.w, self.h))
        else:
            self.bg_image = None
            self.bg_color = (50, 150, 255)  # Fallback color

        # --- Fonts ---
        self.title_font = pygame.font.SysFont("Comic Sans MS", 72, bold=True)
        self.button_font = pygame.font.SysFont("Comic Sans MS", 36, bold=True)

        # --- Top buttons ---
        cx = self.w // 2
        start_y = self.h // 2 - 100
        bw, bh = 360, 70
        gap = 20

        self.buttons = [
            Button(
                (cx - bw // 2, start_y, bw, bh),
                text="Select Student",
                font=self.button_font,
                bg_color=(255, 255, 0),
                text_color=(255, 255, 255),
                action=self.select_student,
                image_path="assets/images/startgamebutton.png"
            ),
            Button(
                (cx - bw // 2, start_y + (bh + gap), bw, bh),
                text="Start Activity",
                font=self.button_font,
                bg_color=(50, 205, 50),
                text_color=(255, 255, 255),
                action=self.start_activity,
                image_path="assets/images/lessonsbutton.png"
            ),
        ]

        # --- Bottom buttons (Help, Settings, Exit) ---
        button_size = 140
        bottom_margin = 30
        spacing = 30
        y_pos = self.h - button_size - bottom_margin

        help_x = 50
        exit_x = self.w - button_size - 50
        settings_x = (self.w - button_size) // 2

        self.buttons += [
            Button(
                (help_x, y_pos, button_size, button_size),
                action=self.help,
                image_path="assets/images/helpbutton.png"
            ),
            Button(
                (settings_x, y_pos, button_size, button_size),
                action=self.settings,
                image_path="assets/images/Settingsbutton.png"
            ),
            Button(
                (exit_x, y_pos, button_size, button_size),
                action=self.exit_game,
                image_path="assets/images/exitbutton.png"
            )
        ]

        # --- Game state ---
        self.current_screen = "menu"  # 'menu', 'stage_select', 'hidden', 'catch', 'maze', 'puzzle', 'knowledge'
        self.stage_select = None
        self.hidden_game = None
        self.catch_game = None
        self.maze_game = None
        self.puzzle_game = None
        self.knowledge_game = None  # Add this

    # --- Actions ---
    def select_student(self):
        print("Select Student")

    def start_activity(self):
        print("Start Activity - Opening Stage Select")
        self.current_screen = "stage_select"
        self.stage_select = StageSelect(self.screen, self)

    def start_hidden_game(self, stage=2):
        print("Starting Hidden Object Game...")
        self.current_screen = "hidden"
        self.hidden_game = HiddenObjectGame(self.screen)
        self.hidden_game.current_stage = stage

    def start_knowledge_game(self, stage=7):  # Add this method
        print("Starting Knowledge Game...")
        self.current_screen = "knowledge"
        self.knowledge_game = KnowledgeGame(self.screen)
        self.knowledge_game.current_stage = stage

    def help(self):
        print("Help")

    def settings(self):
        print("Settings")

    def exit_game(self):
        pygame.quit()
        raise SystemExit

    # --- Event Loop ---
    def handle_event(self, event):
        if self.current_screen == "menu":
            for b in self.buttons:
                b.handle_event(event)

        elif self.current_screen == "stage_select" and self.stage_select:
            result = self.stage_select.handle_event(event)
            if result == "back":
                self.current_screen = "menu"
                self.stage_select = None
            # The stage_select.start_game() already sets the current_screen and game instance

        elif self.current_screen == "hidden" and self.hidden_game:
            result = self.hidden_game.handle_event(event)
            if result == "exit":
                self.current_screen = "stage_select"
                self.hidden_game = None

        elif self.current_screen == "catch" and self.catch_game:
            result = self.catch_game.handle_event(event)
            if result == "back" or result == "exit":
                self.current_screen = "stage_select"
                self.catch_game = None

        elif self.current_screen == "maze" and self.maze_game:
            result = self.maze_game.handle_event(event)
            if result == "back" or result == "exit":
                self.current_screen = "stage_select"
                self.maze_game = None

        elif self.current_screen == "puzzle" and self.puzzle_game:
            result = self.puzzle_game.handle_event(event)
            if result == "exit":
                self.current_screen = "stage_select"
                self.puzzle_game = None

        elif self.current_screen == "knowledge" and self.knowledge_game:  # Add this
            result = self.knowledge_game.handle_event(event)
            if result == "exit":
                self.current_screen = "stage_select"
                self.knowledge_game = None

    # --- Update ---
    def update(self):
        if self.current_screen == "menu":
            for b in self.buttons:
                b.update()

        elif self.current_screen == "stage_select" and self.stage_select:
            self.stage_select.update()

        elif self.current_screen == "hidden" and self.hidden_game:
            self.hidden_game.update()

        elif self.current_screen == "catch" and self.catch_game:
            self.catch_game.update()

        elif self.current_screen == "maze" and self.maze_game:
            self.maze_game.update()

        elif self.current_screen == "puzzle" and self.puzzle_game:
            self.puzzle_game.update()

        elif self.current_screen == "knowledge" and self.knowledge_game:  # Add this
            self.knowledge_game.update()

    # --- Draw ---
    def draw(self):
        if self.current_screen == "menu":
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill(self.bg_color)

            # Draw title
            smart = self.title_font.render("Cognitive", True, (255, 255, 255))
            play = self.title_font.render("Play", True, (255, 215, 0))
            total_width = smart.get_width() + play.get_width() + 10
            x = self.w // 2 - total_width // 2
            self.screen.blit(smart, (x, 40))
            self.screen.blit(play, (x + smart.get_width() + 10, 40))

            for b in self.buttons:
                b.draw(self.screen)

        elif self.current_screen == "stage_select" and self.stage_select:
            self.stage_select.draw()

        elif self.current_screen == "hidden" and self.hidden_game:
            self.hidden_game.draw()

        elif self.current_screen == "catch" and self.catch_game:
            self.catch_game.draw()

        elif self.current_screen == "maze" and self.maze_game:
            self.maze_game.draw()

        elif self.current_screen == "puzzle" and self.puzzle_game:
            self.puzzle_game.draw()

        elif self.current_screen == "knowledge" and self.knowledge_game:  # Add this
            if not self.knowledge_game.draw():
                self.current_screen = "stage_select"
                self.knowledge_game = None