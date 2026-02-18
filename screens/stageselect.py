# screens/stageselect.py
import pygame
import os
from screens.catchgame import CatchGame
from screens.mazegame import MazeGame
from screens.hiddenobject import HiddenObjectGame
from screens.minipuzzle import MiniPuzzleGame
from screens.knowledgegame import KnowledgeGame


class StageSelect:
    def __init__(self, screen, main_menu_instance):
        self.screen = screen
        self.w, self.h = screen.get_size()
        self.main_menu = main_menu_instance

        # --- Use menu background ---
        self.bg_image = self.main_menu.bg_image
        self.bg_color = getattr(self.main_menu, 'bg_color', (50, 150, 255))

        # Fonts
        self.title_font = pygame.font.SysFont("Comic Sans MS", 64, bold=True)
        self.stage_font = pygame.font.SysFont("Comic Sans MS", 48, bold=True)
        self.game_font = pygame.font.SysFont("Comic Sans MS", 24, bold=True)
        self.small_font = pygame.font.SysFont("Comic Sans MS", 20)

        # Colors for stages
        self.stage_colors = [
            (255, 140, 0),  # Orange - Stage 1 (Catch Game)
            (255, 215, 0),  # Gold - Stage 2 (Hidden Object Game)
            (50, 205, 50),  # Lime Green - Stage 3 (Mini Puzzle Game)
            (150, 150, 150),  # Gray - Stage 4 (Coming Soon)
            (150, 150, 150),  # Gray - Stage 5 (Coming Soon)
            (150, 150, 150),  # Gray - Stage 6 (Coming Soon)
            (147, 112, 219),  # Purple - Stage 7 (Knowledge Game)
            (65, 105, 225),  # Royal Blue - Stage 8 (Maze Game)
        ]

        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.BLACK = (0, 0, 0)
        self.GRAY = (150, 150, 150)

        # Exit button from menu
        self.exit_rect = self.main_menu.buttons[-1].rect  # assume last bottom button is Exit
        self.exit_hover = False

        # Stage selection buttons
        self.stage_buttons = []
        self.create_stage_buttons()

        # Game instances
        self.current_game = None

    def create_stage_buttons(self):
        """Create 8 stage selection buttons"""
        button_width = 150
        button_height = 150
        gap_x = 40

        # Calculate positions for 4 columns
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
            else:  # Stage 4
                game_type = None
                game_name = "Coming Soon"
                icon = "🔒"
                locked = True

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
            else:  # Stages 5 and 6
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
        """Start the selected game"""
        print(f"Starting {game_type} on Stage {stage}")

        if game_type == "catch":
            self.current_game = CatchGame(self.screen)
            self.current_game.current_stage = stage
            self.main_menu.current_screen = "catch"
            self.main_menu.catch_game = self.current_game

        elif game_type == "maze":
            self.current_game = MazeGame(self.screen)
            self.current_game.current_stage = stage
            self.main_menu.current_screen = "maze"
            self.main_menu.maze_game = self.current_game

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

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEMOTION:
            self.exit_hover = self.exit_rect.collidepoint(event.pos)
            for button in self.stage_buttons:
                button["hover"] = button["rect"].collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check exit button
                if self.exit_rect.collidepoint(event.pos):
                    return "back"

                # Check stage buttons
                for button in self.stage_buttons:
                    if button["rect"].collidepoint(event.pos):
                        if not button["locked"]:
                            self.start_game(button["game"], button["stage"])
                            return None
                        else:
                            print(f"Stage {button['stage']} is locked - Coming Soon!")

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"

        return None

    def update(self):
        """Update current game if active"""
        if self.current_game:
            self.current_game.update()

    def draw(self):
        """Draw everything to the screen"""
        # Background from menu
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(self.bg_color)

        # Title
        title = self.title_font.render("SELECT STAGE", True, self.WHITE)
        title_rect = title.get_rect(center=(self.w // 2, 80))
        shadow = self.title_font.render("SELECT STAGE", True, self.BLACK)
        shadow_rect = shadow.get_rect(center=(self.w // 2 + 4, 84))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(title, title_rect)

        # "Available Now" text
        available_title = self.game_font.render("AVAILABLE NOW", True, (100, 255, 100))
        available_rect = available_title.get_rect(center=(self.w // 2, self.h // 2 - 180))
        self.screen.blit(available_title, available_rect)

        # Draw Exit button from menu
        if hasattr(self.main_menu, 'buttons') and len(self.main_menu.buttons) > 0:
            exit_button = self.main_menu.buttons[-1]  # Last bottom button is Exit
            exit_button.draw(self.screen)

        # Draw stage buttons
        for button in self.stage_buttons:
            color = button["color"]
            if button["hover"] and not button["locked"]:
                color = tuple(min(c + 40, 255) for c in color)
                # Draw highlight
                pygame.draw.rect(self.screen, self.WHITE, button["rect"].inflate(10, 10), border_radius=18)

            # Draw button background
            pygame.draw.rect(self.screen, color, button["rect"], border_radius=15)

            # Draw button border
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
            name_color = self.WHITE if not button["locked"] else (180, 180, 180)
            game_text = self.small_font.render(button["game_name"], True, name_color)
            game_rect = game_text.get_rect(center=(button["rect"].centerx, button["rect"].bottom - 25))
            self.screen.blit(game_text, game_rect)

        # Instructions
        inst_text = self.small_font.render("Click on Stage 1, 2, 3, 7, or 8 to play!", True, self.WHITE)
        inst_rect = inst_text.get_rect(center=(self.w // 2, self.h - 50))

        # Draw instruction background
        bg_rect = inst_rect.inflate(20, 10)
        bg_rect.center = inst_rect.center
        pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)
        pygame.draw.rect(self.screen, self.WHITE, bg_rect, 2)
        self.screen.blit(inst_text, inst_rect)

        pygame.display.flip()