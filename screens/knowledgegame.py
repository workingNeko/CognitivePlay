# screens/knowledgegame.py
import pygame
import os
import time
import json


class KnowledgeGame:
    def __init__(self, screen):
        self.screen = screen
        self.w, self.h = screen.get_size()

        self.FPS = 60
        self.clock = pygame.time.Clock()

        # Game state
        self.running = True
        self.current_slide = 0
        self.show_feedback = False
        self.feedback_text = ""
        self.feedback_timer = 0
        self.feedback_duration = 90  # frames
        self.selected_choice = None
        self.save_positions = []  # For snowman differences
        self.show_congratulations = False
        self.congrats_timer = 0

        # ================= COLORS =================
        self.WHITE = (255, 255, 255)
        self.BLACK = (30, 30, 30)
        self.RED = (255, 99, 71)
        self.BLUE = (100, 149, 237)
        self.GREEN = (34, 139, 34)
        self.ORANGE = (255, 165, 0)
        self.YELLOW = (255, 215, 0)
        self.PURPLE = (147, 112, 219)
        self.GRAY = (128, 128, 128)
        self.GOLD = (255, 215, 0)

        # ================= BACKGROUND =================
        assets_path = os.path.join("assets", "images")
        bg_path = os.path.join(assets_path, "menu_background.png")
        if os.path.exists(bg_path):
            self.bg_image = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (self.w, self.h))
            self.use_bg = True
        else:
            self.use_bg = False
            self.bg_color = (100, 150, 200)

        # ================= LOAD EXIT BUTTON IMAGE =================
        self.exit_button_img = None
        exit_img_path = os.path.join(assets_path, "exitbutton.png")
        if os.path.exists(exit_img_path):
            try:
                self.exit_button_img = pygame.image.load(exit_img_path).convert_alpha()
                print("Loaded exit button image")
            except:
                print("Could not load exit button image")

        # ================= LOAD SLIDE IMAGES =================
        self.slide_images = {}
        self.load_slide_images()

        # ================= BUTTONS =================
        # Exit button with image
        if self.exit_button_img:
            self.exit_button_img = pygame.transform.scale(self.exit_button_img, (120, 60))
            self.exit_rect = self.exit_button_img.get_rect(topleft=(20, 20))
        else:
            self.exit_rect = pygame.Rect(20, 20, 120, 60)

        self.exit_hover = False

        # Save button for snowman slide
        self.save_button_rect = pygame.Rect(self.w - 200, self.h - 100, 150, 60)
        self.save_hover = False

        # ================= FONTS =================
        self.title_font = pygame.font.SysFont("comicsansms", 48, bold=True)
        self.question_font = pygame.font.SysFont("comicsansms", 36, bold=True)
        self.choice_font = pygame.font.SysFont("comicsansms", 32, bold=True)
        self.feedback_font = pygame.font.SysFont("comicsansms", 36, bold=True)
        self.congrats_font = pygame.font.SysFont("comicsansms", 48, bold=True)
        self.small_font = pygame.font.SysFont("comicsansms", 24)

        # ================= SLIDE DEFINITIONS =================
        self.slides = [
            # Slide 0: Name animals - Dog
            {
                "type": "animals",
                "question": None,
                "image": "dog.png",
                "choices": ["DOG", "CAT"],
                "correct": 0,
                "feedback_correct": "Good job! Keep it up!",
                "feedback_wrong": "Try again! You can do it!"
            },
            # Slide 1: Name animals - Cat
            {
                "type": "animals",
                "question": None,
                "image": "cat.png",
                "choices": ["DOG", "CAT"],
                "correct": 1,
                "feedback_correct": "Good job! Keep it up!",
                "feedback_wrong": "Try again! You can do it!"
            },
            # Slide 2: Items use - Spoon and Fork
            {
                "type": "items",
                "question": None,
                "image": "spoonandfork.png",
                "choices": ["EATING", "DRINKING"],
                "correct": 0,
                "feedback_correct": "Good job! Keep it up!",
                "feedback_wrong": "Try again! You can do it!"
            },
            # Slide 3: Items use - Glass of Water
            {
                "type": "items",
                "question": None,
                "image": "glassofwater.png",
                "choices": ["EATING", "DRINKING"],
                "correct": 1,
                "feedback_correct": "Good job! Keep it up!",
                "feedback_wrong": "Try again! You can do it!"
            },
            # Slide 4: Opposites - Big
            {
                "type": "opposites",
                "question": "Which is BIG?",
                "image": "dogandcat.png",
                "choices": ["DOG", "CAT"],
                "correct": 0,
                "feedback_correct": "Good job! Keep it up!",
                "feedback_wrong": "The dog is bigger. Let's try the next one!"
            },
            # Slide 5: Opposites - Small
            {
                "type": "opposites",
                "question": "Which is SMALL?",
                "image": "dogandcat.png",
                "choices": ["DOG", "CAT"],
                "correct": 1,
                "feedback_correct": "Good job! Keep it up!",
                "feedback_wrong": "The cat is smaller. Let's try the next one!"
            },
            # Slide 6: What's wrong - Snowman (with drag and drop)
            {
                "type": "snowman",
                "question": "What's wrong in this picture?",
                "image": "snowman.png",
                "choices": None,
                "correct": None,
                "feedback_correct": "Good job! Keep it up!",
                "feedback_wrong": "Try again! You can do it!",
                "differences": 3
            },
            # Slide 7: Uppercase/Lowercase - A
            {
                "type": "letters",
                "question": "Match the Letter",
                "image": "a.png",
                "choices": ["a", "b"],
                "correct": 0,
                "feedback_correct": "Good job! Keep it up!",
                "feedback_wrong": "Try again! You can do it!"
            },
            # Slide 8: Uppercase/Lowercase - B
            {
                "type": "letters",
                "question": "Match the Letter",
                "image": "b.png",
                "choices": ["b", "c"],
                "correct": 0,
                "feedback_correct": "Good job! Keep it up!",
                "feedback_wrong": "Try again! You can do it!"
            },
            # Slide 9: Uppercase/Lowercase - C
            {
                "type": "letters",
                "question": "Match the Letter",
                "image": "c.png",
                "choices": ["a", "c"],
                "correct": 1,
                "feedback_correct": "Good job! Keep it up!",
                "feedback_wrong": "Try again! You can do it!"
            }
        ]

        # Create choice buttons
        self.choice_buttons = []
        self.create_choice_buttons()

        # Snowman drag and drop circles
        self.snowman_circles = []
        self.dragging_circle = None
        self.snowman_saved = False  # Flag to track if snowman slide was completed

        # ================= IMAGE RECT =================
        image_width = 400
        image_height = 300
        self.image_rect = pygame.Rect(
            self.w // 2 - image_width // 2,
            self.h // 2 - image_height // 2 - 50,
            image_width,
            image_height
        )

    def load_slide_images(self):
        """Load all the PNG images for the slides"""
        assets_path = os.path.join("assets", "images")
        image_files = ["dog.png", "cat.png", "dogandcat.png", "spoonandfork.png",
                       "glassofwater.png", "snowman.png", "a.png", "b.png", "c.png"]

        for img_file in image_files:
            img_path = os.path.join(assets_path, img_file)
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    self.slide_images[img_file] = img
                    print(f"Loaded image: {img_file}")
                except:
                    print(f"Could not load image: {img_file}")
            else:
                print(f"Image file not found: {img_path}")

    def create_choice_buttons(self):
        """Create the two choice buttons"""
        button_width = 200
        button_height = 80
        spacing = 50

        left_x = self.w // 2 - button_width - spacing // 2
        right_x = self.w // 2 + spacing // 2

        y_pos = self.h - 150

        self.choice_buttons = [
            {"rect": pygame.Rect(left_x, y_pos, button_width, button_height), "text": "", "index": 0, "hover": False},
            {"rect": pygame.Rect(right_x, y_pos, button_width, button_height), "text": "", "index": 1, "hover": False}
        ]

    def show_feedback_message(self, text, is_correct=True):
        """Show feedback message"""
        self.feedback_text = text
        self.feedback_timer = self.feedback_duration
        self.show_feedback = True

        if is_correct:
            # Move to next slide after correct answer
            if self.current_slide < len(self.slides) - 1:
                self.current_slide += 1
                # Reset snowman flag when leaving snowman slide
                if self.current_slide == 7:  # After snowman slide
                    self.snowman_saved = False
                    self.snowman_circles = []
            else:
                # Last slide - show congratulations
                self.show_congratulations = True
                self.congrats_timer = 180

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Hover effects
            self.exit_hover = self.exit_rect.collidepoint(event.pos)
            self.save_hover = self.save_button_rect.collidepoint(event.pos)

            # Choice button hover (only if not showing feedback)
            if not self.show_feedback and self.slides[self.current_slide]["choices"]:
                for button in self.choice_buttons:
                    button["hover"] = button["rect"].collidepoint(event.pos)

            # Handle dragging for snowman circles
            if self.dragging_circle:
                self.dragging_circle["x"], self.dragging_circle["y"] = event.pos

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check exit button
                if self.exit_rect.collidepoint(event.pos):
                    self.running = False
                    return "exit"

                # Check save button (only on snowman slide)
                if self.current_slide == 6 and self.save_button_rect.collidepoint(event.pos):
                    # Save circle positions to terminal
                    print("\n=== SNOWMAN DIFFERENCE POSITIONS ===")
                    for i, circle in enumerate(self.snowman_circles):
                        print(f"Difference {i + 1}: ({circle['x']}, {circle['y']})")
                    print("=====================================\n")

                    # Mark as saved and move to next slide
                    self.snowman_saved = True
                    self.show_feedback_message("Good job! Keep it up!", True)
                    return None

                # Check choice buttons (if not showing feedback)
                if not self.show_feedback and self.slides[self.current_slide]["choices"]:
                    for button in self.choice_buttons:
                        if button["rect"].collidepoint(event.pos):
                            self.check_answer(button["index"])
                            break

                # Handle snowman circle creation/dragging (only on snowman slide and not saved yet)
                if self.current_slide == 6 and not self.snowman_saved:
                    # Check if clicking on existing circle
                    circle_clicked = False
                    for circle in self.snowman_circles:
                        dist = ((circle["x"] - event.pos[0]) ** 2 + (circle["y"] - event.pos[1]) ** 2) ** 0.5
                        if dist < circle["radius"]:
                            self.dragging_circle = circle
                            circle_clicked = True
                            break

                    # If not clicking on circle, create new one (max 3)
                    if not circle_clicked and len(self.snowman_circles) < 3:
                        self.snowman_circles.append({
                            "x": event.pos[0],
                            "y": event.pos[1],
                            "radius": 20,
                            "color": self.RED
                        })

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_circle = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
                return "exit"

        return None

    def check_answer(self, choice_index):
        """Check if the selected answer is correct"""
        slide = self.slides[self.current_slide]

        if choice_index == slide["correct"]:
            self.show_feedback_message(slide["feedback_correct"], True)
        else:
            self.show_feedback_message(slide["feedback_wrong"], False)

    def update(self):
        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
        else:
            self.show_feedback = False

        # Update congrats timer
        if self.congrats_timer > 0:
            self.congrats_timer -= 1

    def draw_image(self, image_filename):
        """Draw the actual image instead of placeholder"""
        if image_filename in self.slide_images:
            img = self.slide_images[image_filename]
            # Scale image to fit the image_rect while preserving aspect ratio
            img_aspect = img.get_width() / img.get_height()
            rect_aspect = self.image_rect.width / self.image_rect.height

            if img_aspect > rect_aspect:
                # Image is wider than rect - scale to width
                scaled_width = self.image_rect.width
                scaled_height = int(scaled_width / img_aspect)
            else:
                # Image is taller than rect - scale to height
                scaled_height = self.image_rect.height
                scaled_width = int(scaled_height * img_aspect)

            scaled_img = pygame.transform.scale(img, (scaled_width, scaled_height))

            # Center the scaled image in the image_rect
            x = self.image_rect.x + (self.image_rect.width - scaled_width) // 2
            y = self.image_rect.y + (self.image_rect.height - scaled_height) // 2

            self.screen.blit(scaled_img, (x, y))

            # Draw a border around the image
            pygame.draw.rect(self.screen, self.BLACK, self.image_rect, 3, border_radius=15)
        else:
            # Fallback to placeholder if image not found
            pygame.draw.rect(self.screen, self.GRAY, self.image_rect, border_radius=15)
            pygame.draw.rect(self.screen, self.BLACK, self.image_rect, 3, border_radius=15)

            # Draw filename as label
            label = self.small_font.render(f"Missing: {image_filename}", True, self.WHITE)
            label_rect = label.get_rect(center=self.image_rect.center)
            self.screen.blit(label, label_rect)

    def draw_choice_buttons(self, slide):
        """Draw the two choice buttons"""
        if not slide["choices"]:
            return

        # Update button texts
        for i, button in enumerate(self.choice_buttons):
            if i < len(slide["choices"]):
                button["text"] = slide["choices"][i]

        # Draw buttons
        for button in self.choice_buttons:
            # Button background
            color = self.BLUE if button["hover"] and not self.show_feedback else self.PURPLE
            pygame.draw.rect(self.screen, color, button["rect"], border_radius=15)
            pygame.draw.rect(self.screen, self.BLACK, button["rect"], 3, border_radius=15)

            # Button text
            text = self.choice_font.render(button["text"], True, self.WHITE)
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)

    def draw_feedback(self):
        """Draw feedback message"""
        if self.show_feedback and self.feedback_text:
            # Create background
            feedback_surf = self.feedback_font.render(self.feedback_text, True, self.WHITE)
            feedback_rect = feedback_surf.get_rect(center=(self.w // 2, self.h // 2))

            # Draw bubble
            bubble_rect = feedback_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, self.BLACK, bubble_rect, border_radius=20)
            pygame.draw.rect(self.screen, self.GOLD, bubble_rect, 4, border_radius=20)

            # Draw text
            self.screen.blit(feedback_surf, feedback_rect)

    def draw_congratulations(self):
        """Draw congratulations message at the end"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Draw congratulations text
        congrats_text = self.congrats_font.render("CONGRATULATIONS!", True, self.GOLD)
        congrats_rect = congrats_text.get_rect(center=(self.w // 2, self.h // 2 - 50))
        self.screen.blit(congrats_text, congrats_rect)

        congrats_text2 = self.feedback_font.render("Press EXIT to go back", True, self.WHITE)
        congrats_rect2 = congrats_text2.get_rect(center=(self.w // 2, self.h // 2 + 50))
        self.screen.blit(congrats_text2, congrats_rect2)

    def draw_snowman_circles(self):
        """Draw draggable circles for snowman differences"""
        for i, circle in enumerate(self.snowman_circles):
            # Draw circle
            pygame.draw.circle(self.screen, circle["color"],
                               (circle["x"], circle["y"]), circle["radius"])
            pygame.draw.circle(self.screen, self.BLACK,
                               (circle["x"], circle["y"]), circle["radius"], 2)

            # Draw number
            num_text = self.small_font.render(str(i + 1), True, self.WHITE)
            num_rect = num_text.get_rect(center=(circle["x"], circle["y"]))
            self.screen.blit(num_text, num_rect)

    def draw_save_button(self):
        """Draw save button for snowman slide"""
        color = self.GREEN if self.save_hover else self.BLUE
        pygame.draw.rect(self.screen, color, self.save_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.BLACK, self.save_button_rect, 2, border_radius=10)

        save_text = self.choice_font.render("SAVE", True, self.WHITE)
        save_rect = save_text.get_rect(center=self.save_button_rect.center)
        self.screen.blit(save_text, save_rect)

    def draw(self):
        # Draw background
        if self.use_bg:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(self.bg_color)

        current_slide = self.slides[self.current_slide]

        # Draw title
        if current_slide["type"] == "animals":
            title = "Name the Animal"
        elif current_slide["type"] == "items":
            title = "What is it used for?"
        elif current_slide["type"] == "opposites":
            title = "Opposites"
        elif current_slide["type"] == "snowman":
            title = "What's Wrong?"
        elif current_slide["type"] == "letters":
            title = "Uppercase/Lowercase Match"
        else:
            title = "Knowledge Game"

        title_surf = self.title_font.render(title, True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.w // 2, 80))
        self.screen.blit(title_surf, title_rect)

        # Draw question if exists
        if current_slide["question"]:
            question_surf = self.question_font.render(current_slide["question"], True, self.BLACK)
            question_rect = question_surf.get_rect(center=(self.w // 2, 150))
            self.screen.blit(question_surf, question_rect)

        # Draw the actual image
        self.draw_image(current_slide["image"])

        # Draw choice buttons if slide has choices and not showing feedback
        if current_slide["choices"] and not self.show_feedback:
            self.draw_choice_buttons(current_slide)

        # Draw snowman circles and save button for snowman slide (if not saved)
        if current_slide["type"] == "snowman" and not self.snowman_saved:
            self.draw_snowman_circles()
            self.draw_save_button()

            # Instructions for snowman
            inst_text = f"Drag circles to mark differences ({len(self.snowman_circles)}/3 placed)"
            inst_surf = self.small_font.render(inst_text, True, self.BLACK)
            inst_rect = inst_surf.get_rect(center=(self.w // 2, self.h - 50))
            self.screen.blit(inst_surf, inst_rect)
        elif current_slide["type"] == "snowman" and self.snowman_saved:
            # Show message that slide is completed
            completed_text = self.feedback_font.render("Slide Completed!", True, self.GREEN)
            completed_rect = completed_text.get_rect(center=(self.w // 2, self.h - 50))
            self.screen.blit(completed_text, completed_rect)

        # Draw exit button
        if self.exit_button_img:
            if self.exit_hover:
                hover_img = pygame.transform.scale(self.exit_button_img,
                                                   (int(self.exit_rect.width * 1.05),
                                                    int(self.exit_rect.height * 1.05)))
                hover_rect = hover_img.get_rect(center=self.exit_rect.center)
                self.screen.blit(hover_img, hover_rect)
            else:
                self.screen.blit(self.exit_button_img, self.exit_rect)
        else:
            exit_color = (200, 50, 50) if self.exit_hover else (255, 100, 100)
            pygame.draw.rect(self.screen, exit_color, self.exit_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.BLACK, self.exit_rect, 2, border_radius=8)

        # Draw slide counter
        slide_text = self.small_font.render(f"Slide {self.current_slide + 1}/{len(self.slides)}", True, self.BLACK)
        self.screen.blit(slide_text, (self.w - 150, 20))

        # Draw feedback message
        self.draw_feedback()

        # Draw congratulations if on last slide and correct
        if self.show_congratulations:
            self.draw_congratulations()

        pygame.display.flip()
        self.clock.tick(self.FPS)
        return self.running