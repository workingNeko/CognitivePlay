import pygame
import os
from ui.button import Button


class NameAndRememberGame:
    """Stage 4 game - integrated with StageSelect"""

    def __init__(self, screen, main_menu_instance=None):
        self.screen = screen
        self.main_menu = main_menu_instance
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.clock = pygame.time.Clock()

        # Initialize current_stage
        self.current_stage = 4

        # ================= FONTS =================
        self.title_font = pygame.font.SysFont("comicsansms", 48, bold=True)
        self.label_font = pygame.font.SysFont("comicsansms", 36, bold=True)
        self.word_font = pygame.font.SysFont("comicsansms", 72, bold=True)
        self.button_font = pygame.font.SysFont("comicsansms", 32, bold=True)
        self.feedback_font = pygame.font.SysFont("comicsansms", 36, bold=True)
        self.small_font = pygame.font.SysFont("comicsansms", 24)

        # ================= COLORS =================
        self.WHITE = (255, 255, 255)
        self.BLACK = (30, 30, 30)
        self.GRAY = (200, 200, 200)
        self.DARK_GRAY = (128, 128, 128)
        self.GREEN = (34, 139, 34)
        self.RED = (255, 99, 71)
        self.BLUE = (100, 149, 237)
        self.PURPLE = (147, 112, 219)
        self.YELLOW = (255, 215, 0)
        self.ORANGE = (255, 165, 0)
        self.LIGHT_BLUE = (173, 216, 230)

        # Fixed sequences
        self.animals = ["DOG", "CAT"]
        self.colors = ["RED", "BLUE", "YELLOW"]
        self.vegetables = ["CARROT", "TOMATO", "EGGPLANT"]

        # Category titles and labels
        self.category_titles = {
            "naming_animals": "Name the Animals",
            "naming_colors": "Name the Colors",
            "naming_vegetables": "Name the Vegetables",
            "watch_animals": "Watch the Animals",
            "watch_colors": "Watch the Colors",
            "watch_vegetables": "Watch the Vegetables",
            "imitate_animals": "Your Turn - Animals",
            "imitate_colors": "Your Turn - Colors",
            "imitate_vegetables": "Your Turn - Vegetables"
        }

        # Game state
        self.state = "naming_animals"
        self.current_index = 0
        self.player_index = 0
        self.watch_timer = 0
        self.watch_index = 0
        self.feedback = ""
        self.feedback_timer = 0
        self.feedback_duration = 90
        self.show_feedback = False
        self.current_sequence = []
        self.watch_state = ""
        self.next_state = ""

        # Button rects list (for multiple buttons)
        self.buttons = []

        # ================= BACKGROUND =================
        assets_path = os.path.join("assets", "images")
        bg_path = os.path.join(assets_path, "menu_background.png")
        try:
            if os.path.exists(bg_path):
                self.bg_image = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.scale(self.bg_image, (self.WIDTH, self.HEIGHT))
                self.use_bg = True
            else:
                self.use_bg = False
                self.bg_color = (100, 150, 200)
        except:
            self.use_bg = False
            self.bg_color = (100, 150, 200)

        # ================= EXIT BUTTON =================
        btn_size = 80
        try:
            self.exit_button = Button(
                (20, 20, btn_size, btn_size),  # Left side
                text="X",
                action=None,
                image_path=os.path.join(assets_path, "exitbutton.png")
            )
            self.exit_fallback = False
        except:
            self.exit_button = pygame.Rect(20, 20, btn_size, btn_size)
            self.exit_fallback = True
        self.exit_hover = False

        # ================= IMAGE PLACEHOLDER RECT =================
        self.image_rect = pygame.Rect(
            self.WIDTH // 2 - 200,
            self.HEIGHT // 2 - 150 - 30,
            400,
            300
        )

    # -------------------- Helper Methods --------------------
    def draw_text(self, text, font, color, x, y, center=True):
        """Safely draw text"""
        if text and font:
            img = font.render(str(text), True, color)
            if center:
                rect = img.get_rect(center=(x, y))
            else:
                rect = img.get_rect(topleft=(x, y))
            self.screen.blit(img, rect)
            return rect
        return None

    def draw_image_placeholder(self, text):
        """Draw a rectangle as image placeholder with text"""
        # Draw placeholder rectangle
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, self.image_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.BLACK, self.image_rect, 3, border_radius=15)

        # Draw placeholder text
        if text:
            self.draw_text(text, self.word_font, self.BLACK,
                           self.image_rect.centerx, self.image_rect.centery)

    def create_buttons(self):
        """Create centered buttons based on current state"""
        self.buttons = []

        # Determine words and positions based on state
        if self.state == "naming_animals" or self.state == "imitate_animals":
            words = self.animals
        elif self.state == "naming_colors" or self.state == "imitate_colors":
            words = self.colors
        elif self.state == "naming_vegetables" or self.state == "imitate_vegetables":
            words = self.vegetables
        else:
            return

        # Add WRONG button for naming stages
        if self.state.startswith("naming"):
            if self.state == "naming_animals" or self.state == "naming_colors" or self.state == "naming_vegetables":
                # For naming stages, we have correct word + WRONG button
                correct_word = words[self.current_index]

                button_width = 180
                button_height = 80
                spacing = 30

                # Calculate positions for 2 buttons
                total_width = 2 * button_width + spacing
                start_x = self.WIDTH // 2 - total_width // 2
                y_pos = self.HEIGHT - 150

                # Correct button
                self.buttons.append({
                    "rect": pygame.Rect(start_x, y_pos, button_width, button_height),
                    "text": correct_word,
                    "index": 0,
                    "is_correct": True,
                    "hover": False,
                    "color": self.GREEN
                })

                # Wrong button
                self.buttons.append({
                    "rect": pygame.Rect(start_x + button_width + spacing, y_pos, button_width, button_height),
                    "text": "WRONG",
                    "index": 1,
                    "is_correct": False,
                    "hover": False,
                    "color": self.RED
                })
        else:
            # For imitate stages, show all words
            num_buttons = len(words)
            button_width = 180
            button_height = 80
            spacing = 30

            total_width = num_buttons * button_width + (num_buttons - 1) * spacing
            start_x = self.WIDTH // 2 - total_width // 2
            y_pos = self.HEIGHT - 150

            for i, word in enumerate(words):
                self.buttons.append({
                    "rect": pygame.Rect(start_x + i * (button_width + spacing), y_pos, button_width, button_height),
                    "text": word,
                    "index": i,
                    "hover": False,
                    "color": self.BLUE
                })

    def draw_buttons(self):
        """Draw all action buttons"""
        for button in self.buttons:
            # Button color with hover effect
            color = button["color"]
            if button["hover"] and not self.show_feedback:
                color = tuple(min(c + 40, 255) for c in color)

            # Draw button
            pygame.draw.rect(self.screen, color, button["rect"], border_radius=15)
            pygame.draw.rect(self.screen, self.BLACK, button["rect"], 3, border_radius=15)

            # Draw button text
            self.draw_text(button["text"], self.button_font, self.WHITE,
                           button["rect"].centerx, button["rect"].centery)

    def draw_feedback(self):
        """Draw feedback message in bubble"""
        if self.show_feedback and self.feedback:
            # Create background
            feedback_surf = self.feedback_font.render(self.feedback, True, self.WHITE)
            feedback_rect = feedback_surf.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))

            # Draw bubble
            bubble_rect = feedback_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, self.BLACK, bubble_rect, border_radius=20)
            pygame.draw.rect(self.screen, self.YELLOW, bubble_rect, 4, border_radius=20)

            # Draw text
            self.screen.blit(feedback_surf, feedback_rect)

    def draw_exit_button(self):
        """Draw the exit button"""
        if self.exit_fallback:
            # Fallback drawing
            color = self.RED if self.exit_hover else self.DARK_GRAY
            pygame.draw.rect(self.screen, color, self.exit_button, border_radius=10)
            pygame.draw.rect(self.screen, self.BLACK, self.exit_button, 2, border_radius=10)
            self.draw_text("X", self.button_font, self.WHITE,
                           self.exit_button.centerx, self.exit_button.centery)
        else:
            self.exit_button.draw(self.screen)
            # Draw hover effect
            if self.exit_hover:
                pygame.draw.rect(self.screen, self.WHITE,
                                 self.exit_button.rect.inflate(10, 10), 3, border_radius=10)

    def show_feedback_message(self, text):
        """Show feedback message"""
        self.feedback = text
        self.feedback_timer = self.feedback_duration
        self.show_feedback = True

    # -------------------- Main Methods --------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "exit"

        if event.type == pygame.MOUSEMOTION:
            # Exit button hover
            if self.exit_fallback:
                self.exit_hover = self.exit_button.collidepoint(event.pos)
            else:
                self.exit_hover = self.exit_button.rect.collidepoint(event.pos)

            # Button hover (only if not showing feedback)
            if not self.show_feedback:
                for button in self.buttons:
                    button["hover"] = button["rect"].collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Exit button click
                if self.exit_fallback:
                    if self.exit_button.collidepoint(event.pos):
                        return "exit"
                else:
                    if self.exit_button.rect.collidepoint(event.pos):
                        return "exit"

                # Game buttons (only if not showing feedback)
                if not self.show_feedback:
                    for button in self.buttons:
                        if button["rect"].collidepoint(event.pos):
                            if self.state.startswith("naming"):
                                if button.get("is_correct", False):
                                    self.feedback = "Good!"
                                    self.feedback_timer = 60
                                    self.show_feedback = True
                                    self.current_index += 1

                                    # Check if finished naming stage
                                    if self.state == "naming_animals" and self.current_index >= len(self.animals):
                                        self.current_index = 0
                                        self.state = "watch_animals"
                                    elif self.state == "naming_colors" and self.current_index >= len(self.colors):
                                        self.current_index = 0
                                        self.state = "watch_colors"
                                    elif self.state == "naming_vegetables" and self.current_index >= len(
                                            self.vegetables):
                                        self.current_index = 0
                                        self.state = "watch_vegetables"
                                else:
                                    self.feedback = "Try Again"
                                    self.feedback_timer = 60
                                    self.show_feedback = True

                            elif self.state.startswith("imitate"):
                                # Get current sequence
                                if "animals" in self.state:
                                    self.current_sequence = self.animals
                                elif "colors" in self.state:
                                    self.current_sequence = self.colors
                                elif "vegetables" in self.state:
                                    self.current_sequence = self.vegetables

                                if button["text"] == self.current_sequence[self.player_index]:
                                    self.player_index += 1
                                    if self.player_index >= len(self.current_sequence):
                                        self.feedback = "Great Memory!"
                                        self.feedback_timer = 90
                                        self.show_feedback = True
                                        self.player_index = 0

                                        # Move to next state
                                        if self.state == "imitate_animals":
                                            self.state = "naming_colors"
                                        elif self.state == "imitate_colors":
                                            self.state = "naming_vegetables"
                                        elif self.state == "imitate_vegetables":
                                            self.state = "finished"
                                else:
                                    self.feedback = "Watch Again!"
                                    self.feedback_timer = 90
                                    self.show_feedback = True
                                    self.player_index = 0
                                    self.state = self.watch_state
                            break

        return None

    def update(self):
        self.clock.tick(60)

        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
        else:
            self.show_feedback = False

        # Watch mode animation
        if self.state.startswith("watch"):
            self.watch_timer += 1
            if self.watch_timer % 60 == 0:  # Change every second
                self.watch_index += 1

                # Get current sequence
                if "animals" in self.state:
                    self.current_sequence = self.animals
                elif "colors" in self.state:
                    self.current_sequence = self.colors
                elif "vegetables" in self.state:
                    self.current_sequence = self.vegetables

                # Check if we've shown all words
                if self.watch_index >= len(self.current_sequence):
                    self.watch_index = 0
                    self.watch_timer = 0

                    # Move to imitate mode
                    if self.state == "watch_animals":
                        self.state = "imitate_animals"
                        self.watch_state = "watch_animals"
                    elif self.state == "watch_colors":
                        self.state = "imitate_colors"
                        self.watch_state = "watch_colors"
                    elif self.state == "watch_vegetables":
                        self.state = "imitate_vegetables"
                        self.watch_state = "watch_vegetables"

                    self.player_index = 0

    def draw(self):
        # Draw background
        if self.use_bg:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(self.bg_color)

        # Draw title
        if self.state in self.category_titles:
            self.draw_text(self.category_titles[self.state], self.title_font, self.BLACK,
                           self.WIDTH // 2, 80)

        # Draw mode label
        if self.state.startswith("watch"):
            label = "WATCH CAREFULLY!"
            self.draw_text(label, self.label_font, self.RED, self.WIDTH // 2, 150)
        elif self.state.startswith("imitate"):
            label = "YOUR TURN!"
            self.draw_text(label, self.label_font, self.GREEN, self.WIDTH // 2, 150)

        # Draw image placeholder
        if self.state.startswith("naming"):
            # Show current word in placeholder
            if "animals" in self.state:
                current_word = self.animals[self.current_index]
            elif "colors" in self.state:
                current_word = self.colors[self.current_index]
            elif "vegetables" in self.state:
                current_word = self.vegetables[self.current_index]
            self.draw_image_placeholder(current_word)

        elif self.state.startswith("watch"):
            # Show watching word in placeholder
            if "animals" in self.state:
                watch_word = self.animals[self.watch_index]
            elif "colors" in self.state:
                watch_word = self.colors[self.watch_index]
            elif "vegetables" in self.state:
                watch_word = self.vegetables[self.watch_index]
            self.draw_image_placeholder(watch_word)

        elif self.state.startswith("imitate"):
            # Show placeholder with category
            if "animals" in self.state:
                self.draw_image_placeholder("ANIMAL?")
            elif "colors" in self.state:
                self.draw_image_placeholder("COLOR?")
            elif "vegetables" in self.state:
                self.draw_image_placeholder("VEGETABLE?")

        elif self.state == "finished":
            self.draw_image_placeholder("COMPLETE!")

        # Recreate buttons if needed (for naming stages when index changes)
        if self.state.startswith("naming") or self.state.startswith("imitate"):
            self.create_buttons()

        # Draw buttons
        if (self.state.startswith("naming") or self.state.startswith("imitate")) and not self.show_feedback:
            self.draw_buttons()

        # Draw exit button
        self.draw_exit_button()

        # Draw feedback
        if self.show_feedback:
            self.draw_feedback()

        # Draw finished screen
        if self.state == "finished":
            # Semi-transparent overlay
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            # Congratulations
            self.draw_text("CONGRATULATIONS!", self.title_font, self.YELLOW,
                           self.WIDTH // 2, self.HEIGHT // 2 - 50)
            self.draw_text("You did great!", self.label_font, self.WHITE,
                           self.WIDTH // 2, self.HEIGHT // 2 + 50)

        pygame.display.flip()