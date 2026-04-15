# screens/stageselect.py
import pygame
import os
from screens.catchgame import CatchGame
from screens.mazegame import MazeGame
from screens.hiddenobject import HiddenObjectGame
from screens.minipuzzle import MiniPuzzleGame
from screens.knowledgegame import KnowledgeGame
from screens.nameandremember import NameAndRememberGame
from ui.button import Button  # Import Button class


class StageSelect:
    def __init__(self, screen, main_menu_instance):
        self.screen = screen
        self.w, self.h = screen.get_size()
        self.main_menu = main_menu_instance

        # --- Background ---
        self.bg_image = getattr(self.main_menu, 'bg_image', None)
        self.bg_color = getattr(self.main_menu, 'bg_color', (50, 150, 255))

        # --- Fonts ---
        self.title_font = pygame.font.SysFont("Comic Sans MS", 64, bold=True)
        self.stage_font = pygame.font.SysFont("Comic Sans MS", 48, bold=True)
        self.game_font = pygame.font.SysFont("Comic Sans MS", 24, bold=True)
        self.small_font = pygame.font.SysFont("Comic Sans MS", 20)

        # --- Colors ---
        self.stage_colors = [
            (255, 140, 0),  # Stage 1
            (255, 215, 0),  # Stage 2
            (50, 205, 50),  # Stage 3
            (147, 112, 219),  # Stage 4 unlocked - Name & Remember
            (150, 150, 150),  # Stage 5
            (150, 150, 150),  # Stage 6
            (147, 112, 219),  # Stage 7
            (65, 105, 225),  # Stage 8
        ]

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (150, 150, 150)

        # --- Exit button (on left side) ---
        btn_size = 80
        left_margin = 20  # Changed from right margin to left margin
        try:
            self.exit_button = Button(
                (left_margin, 20, btn_size, btn_size),  # Now on left side
                action=None,  # Will handle manually
                image_path="assets/images/exitbutton.png"
            )
        except:
            # Fallback if Button class fails
            self.exit_button = pygame.Rect(left_margin, 20, btn_size, btn_size)
            self.exit_button_fallback = True
        self.exit_hover = False

        # --- Stage buttons ---
        self.stage_buttons = []
        self.create_stage_buttons()

        # --- Game instance ---
        self.current_game = None

    def create_stage_buttons(self):
        """Create all 8 stage buttons"""
        button_width, button_height, gap_x = 150, 150, 40
        cols = 4
        total_width = cols * button_width + (cols - 1) * gap_x
        start_x = (self.w - total_width) // 2

        # First row (Stages 1-4)
        first_row_y = self.h // 2 - 120
        for i in range(4):
            stage_num = i + 1
            x = start_x + i * (button_width + gap_x)
            if stage_num == 1:
                game_type = "catch"
                game_name = "Catch Game"
                icon = "🎯"
                locked = False
            elif stage_num == 2:
                game_type = "hidden"
                game_name = "Hidden Objects"
                icon = "🔍"
                locked = False
            elif stage_num == 3:
                game_type = "puzzle"
                game_name = "Mini Puzzle"
                icon = "🧩"
                locked = False
            else:  # Stage 4 unlocked
                game_type = "memory"
                game_name = "Name & Remember"
                icon = "🧠"
                locked = False

            self.stage_buttons.append({
                "rect": pygame.Rect(x, first_row_y, button_width, button_height),
                "stage": stage_num,
                "game": game_type,
                "game_name": game_name,
                "color": self.stage_colors[stage_num - 1],
                "hover": False,
                "icon": icon,
                "locked": locked
            })

        # Second row (Stages 5-8)
        second_row_y = self.h // 2 + 80
        for i in range(4):
            stage_num = i + 5
            x = start_x + i * (button_width + gap_x)
            if stage_num == 7:
                game_type = "knowledge"
                game_name = "Knowledge Game"
                icon = "📚"
                locked = False
            elif stage_num == 8:
                game_type = "maze"
                game_name = "Maze Game"
                icon = "🌀"
                locked = False
            else:  # Stages 5 & 6 locked
                game_type = None
                game_name = "Coming Soon"
                icon = "🔒"
                locked = True

            self.stage_buttons.append({
                "rect": pygame.Rect(x, second_row_y, button_width, button_height),
                "stage": stage_num,
                "game": game_type,
                "game_name": game_name,
                "color": self.stage_colors[stage_num - 1],
                "hover": False,
                "icon": icon,
                "locked": locked
            })

    def start_game(self, game_type, stage):
        """Start selected game"""
        if game_type == "catch":
            self.current_game = CatchGame(self.screen)
            self.current_game.current_stage = stage
            self.main_menu.current_screen = "catch"
            self.main_menu.catch_game = self.current_game
        elif game_type == "hidden":
            self.current_game = HiddenObjectGame(self.screen)
            self.current_game.current_stage = stage
            self.main_menu.current_screen = "hidden"
            self.main_menu.hidden_game = self.current_game
        elif game_type == "puzzle":
            self.current_game = MiniPuzzleGame(self.screen)
            self.current_game.current_stage = stage
            self.main_menu.current_screen = "puzzle"
            self.main_menu.puzzle_game = self.current_game
        elif game_type == "knowledge":
            self.current_game = KnowledgeGame(self.screen)
            self.current_game.current_stage = stage
            self.main_menu.current_screen = "knowledge"
            self.main_menu.knowledge_game = self.current_game
        elif game_type == "memory":
            self.current_game = NameAndRememberGame(self.screen, self.main_menu)  # Pass main_menu
            self.current_game.current_stage = stage
            self.main_menu.current_screen = "memory"
            self.main_menu.memory_game = self.current_game
        elif game_type == "maze":  # Add this block
            self.current_game = MazeGame(self.screen)
            self.current_game.current_stage = stage
            self.main_menu.current_screen = "maze"
            self.main_menu.maze_game = self.current_game

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Exit button hover
            if hasattr(self, 'exit_button'):
                if isinstance(self.exit_button, Button):
                    self.exit_hover = self.exit_button.rect.collidepoint(event.pos)
                else:
                    self.exit_hover = self.exit_button.collidepoint(event.pos)

            # Stage buttons hover
            for button in self.stage_buttons:
                button["hover"] = button["rect"].collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check exit button (now on left side)
                if hasattr(self, 'exit_button'):
                    if isinstance(self.exit_button, Button) and self.exit_button.rect.collidepoint(event.pos):
                        return "back"
                    elif isinstance(self.exit_button, pygame.Rect) and self.exit_button.collidepoint(event.pos):
                        return "back"

                # Check stage buttons
                for button in self.stage_buttons:
                    if button["rect"].collidepoint(event.pos):
                        if not button["locked"]:
                            self.start_game(button["game"], button["stage"])
                        else:
                            print(f"Stage {button['stage']} is locked")

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"

        return None

    def update(self):
        if self.current_game:
            self.current_game.update()

    def draw(self):
        # Background
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(self.bg_color)

        # Title
        title = self.title_font.render("SELECT STAGE", True, self.WHITE)
        shadow = self.title_font.render("SELECT STAGE", True, self.BLACK)
        self.screen.blit(shadow, (self.w // 2 - title.get_width() // 2 + 4, 84))
        self.screen.blit(title, (self.w // 2 - title.get_width() // 2, 80))

        # Draw exit button (on left side)
        if hasattr(self, 'exit_button'):
            if isinstance(self.exit_button, Button):
                self.exit_button.draw(self.screen)
            else:
                # Draw fallback exit button
                pygame.draw.rect(self.screen, (255, 0, 0), self.exit_button)
                font = pygame.font.SysFont(None, 50)
                text = font.render("X", True, self.WHITE)
                text_rect = text.get_rect(center=self.exit_button.center)
                self.screen.blit(text, text_rect)

            # Draw hover effect
            if self.exit_hover:
                if isinstance(self.exit_button, Button):
                    pygame.draw.rect(self.screen, self.WHITE, self.exit_button.rect.inflate(10, 10), 3,
                                     border_radius=10)
                else:
                    pygame.draw.rect(self.screen, self.WHITE, self.exit_button.inflate(10, 10), 3, border_radius=10)

        # Draw stage buttons
        for button in self.stage_buttons:
            color = button["color"]
            if button["hover"] and not button["locked"]:
                color = tuple(min(c + 40, 255) for c in color)
                pygame.draw.rect(self.screen, self.WHITE, button["rect"].inflate(10, 10), border_radius=18)

            # Draw button background
            pygame.draw.rect(self.screen, color, button["rect"], border_radius=15)

            # Draw border
            border_color = self.WHITE if not button["locked"] else (80, 80, 80)
            pygame.draw.rect(self.screen, border_color, button["rect"], 4, border_radius=15)

            # Draw icon
            icon_text = self.small_font.render(button["icon"], True, self.WHITE)
            icon_rect = icon_text.get_rect(center=(button["rect"].centerx, button["rect"].y + 30))
            self.screen.blit(icon_text, icon_rect)

            # Draw stage number
            stage_text = self.stage_font.render(str(button["stage"]), True, self.WHITE)
            stage_rect = stage_text.get_rect(center=(button["rect"].centerx, button["rect"].centery - 10))
            self.screen.blit(stage_text, stage_rect)

            # Draw game name
            text_color = self.WHITE if not button["locked"] else (180, 180, 180)
            game_text = self.small_font.render(button["game_name"], True, text_color)
            game_rect = game_text.get_rect(center=(button["rect"].centerx, button["rect"].bottom - 25))
            self.screen.blit(game_text, game_rect)

        pygame.display.flip()