# screens/hiddenobject.py
import pygame
import os
import json
import random
import time


class HiddenObjectGame:
    def __init__(self, screen):
        self.screen = screen
        self.w, self.h = screen.get_size()

        self.FPS = 60
        self.ground_y = self.h - 120
        self.clock = pygame.time.Clock()

        # Game state variables
        self.running = True
        self.last_activity_time = time.time()
        self.idle_timer = 3  # seconds
        self.moving_object_index = None
        self.move_start_time = None
        self.move_duration = 2  # seconds
        self.move_start_pos = None
        self.move_end_pos = None
        self.game_completed = False
        self.show_congrats = False
        self.congrats_timer = 0

        # Collected items section
        self.collected_items = []
        self.collected_area_rect = pygame.Rect(self.w - 200, 100, 150, self.h - 200)
        self.checkmark_font = pygame.font.SysFont("comicsansms", 30)

        # Message popup variables
        self.message = ""
        self.message_timer = 0
        self.message_duration = 120  # frames

        # ================= COLORS =================
        self.WHITE = (255, 255, 255)
        self.BLACK = (30, 30, 30)
        self.RED = (255, 99, 71)
        self.BLUE = (100, 149, 237)
        self.GREEN = (34, 139, 34)
        self.ORANGE = (255, 165, 0)
        self.YELLOW = (255, 215, 0)
        self.PURPLE = (147, 112, 219)
        self.PINK = (255, 182, 193)
        self.CYAN = (0, 255, 255)
        self.BROWN = (139, 69, 19)
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

        # ================= LOAD EQUIPMENT IMAGES =================
        self.equipment_images = {}
        self.load_equipment_images()

        # ================= LOAD TOY IMAGES =================
        self.toy_images = {}
        self.load_toy_images()

        # ================= BUTTONS =================
        # Exit button with image
        if self.exit_button_img:
            self.exit_button_img = pygame.transform.scale(self.exit_button_img, (120, 60))
            self.exit_rect = self.exit_button_img.get_rect(topleft=(20, 20))
        else:
            self.exit_rect = pygame.Rect(20, 20, 120, 60)

        self.exit_hover = False

        # ================= FONTS =================
        self.title_font = pygame.font.SysFont("comicsansms", 36, bold=True)
        self.text_font = pygame.font.SysFont("comicsansms", 24)
        self.small_font = pygame.font.SysFont("comicsansms", 20)
        self.message_font = pygame.font.SysFont("comicsansms", 22, bold=True)
        self.congrats_font = pygame.font.SysFont("comicsansms", 48, bold=True)

        # ================= LARGE PLACEHOLDERS WITH IMAGES =================
        self.placeholders = [
            {"name": "SWING", "rect": pygame.Rect(366, 439, 220, 250), "image": "swing.png", "alpha": 255},
            {"name": "SEESAW", "rect": pygame.Rect(845, 700, 300, 180), "image": "seesaw.png", "alpha": 255},
            {"name": "BARS", "rect": pygame.Rect(1241, 551, 180, 200), "image": "mbars.png", "alpha": 255},
            {"name": "SLIDE", "rect": pygame.Rect(969, 412, 160, 180), "image": "slide.png", "alpha": 255},
        ]

        # ================= CLICKABLE TOY IMAGES =================
        self.toys = [
            {"name": "Ball", "rect": pygame.Rect(1014, 770, 80, 80), "image": "ball.png",
             "collected": False},
            {"name": "Apple", "rect": pygame.Rect(126, 395, 50, 50), "image": "apple.png",
             "collected": False},
            {"name": "Teddy Bear", "rect": pygame.Rect(1252, 625, 90, 90), "image": "tbear.png",
             "collected": False},
            {"name": "Car", "rect": pygame.Rect(968, 500, 100, 60), "image": "car.png",
             "collected": False},
            {"name": "Doll", "rect": pygame.Rect(340, 578, 70, 100), "image": "doll.png",
             "collected": False},
        ]

    def load_equipment_images(self):
        """Load the PNG images for playground equipment"""
        assets_path = os.path.join("assets", "images")
        image_files = ["swing.png", "seesaw.png", "mbars.png", "slide.png"]

        for img_file in image_files:
            img_path = os.path.join(assets_path, img_file)
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    self.equipment_images[img_file] = img
                    print(f"Loaded equipment: {img_file}")
                except:
                    print(f"Could not load equipment: {img_file}")
            else:
                print(f"Equipment file not found: {img_path}")

    def load_toy_images(self):
        """Load the PNG images for toys"""
        assets_path = os.path.join("assets", "images")
        toy_files = ["ball.png", "apple.png", "tbear.png", "car.png", "doll.png"]

        for img_file in toy_files:
            img_path = os.path.join(assets_path, img_file)
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    self.toy_images[img_file] = img
                    print(f"Loaded toy: {img_file}")
                except:
                    print(f"Could not load toy: {img_file}")
            else:
                print(f"Toy file not found: {img_path}")

    def show_message(self, text):
        """Display a popup message"""
        self.message = text
        self.message_timer = self.message_duration

    def get_uncollected_toys(self):
        """Return list of toys that haven't been collected yet"""
        return [toy for toy in self.toys if not toy["collected"]]

    def start_idle_movement(self):
        """Start moving a random uncollected toy"""
        uncollected = self.get_uncollected_toys()
        if uncollected and not self.game_completed:
            self.moving_object_index = random.randint(0, len(uncollected) - 1)
            toy = uncollected[self.moving_object_index]

            # Store original position and set movement parameters
            self.move_start_pos = (toy["rect"].x, toy["rect"].y)
            self.move_start_time = time.time()

            # Calculate end position (small movement in random direction)
            dx = random.randint(-30, 30)
            dy = random.randint(-30, 30)
            self.move_end_pos = (
                max(20, min(self.w - toy["rect"].width - 20, self.move_start_pos[0] + dx)),
                max(50, min(self.h - toy["rect"].height - 50, self.move_start_pos[1] + dy))
            )

    def update_idle_movement(self):
        """Update the position of the moving toy"""
        if self.moving_object_index is not None and self.move_start_time and not self.game_completed:
            uncollected = self.get_uncollected_toys()
            if uncollected and self.moving_object_index < len(uncollected):
                toy = uncollected[self.moving_object_index]

                # Calculate progress (0 to 1)
                elapsed = time.time() - self.move_start_time
                progress = min(1.0, elapsed / self.move_duration)

                # Interpolate position
                if progress < 1.0:
                    # Move toy
                    x = self.move_start_pos[0] + (self.move_end_pos[0] - self.move_start_pos[0]) * progress
                    y = self.move_start_pos[1] + (self.move_end_pos[1] - self.move_start_pos[1]) * progress
                    toy["rect"].x = int(x)
                    toy["rect"].y = int(y)
                else:
                    # Movement complete
                    self.moving_object_index = None
                    self.move_start_time = None
                    self.last_activity_time = time.time()

    # ======================================================
    # EVENTS
    # ======================================================
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.exit_hover = self.exit_rect.collidepoint(event.pos)

            # Reset idle timer on mouse movement
            if not self.game_completed:
                self.last_activity_time = time.time()
                # Stop any ongoing movement when user moves mouse
                self.moving_object_index = None
                self.move_start_time = None

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check exit button first
                if self.exit_rect.collidepoint(event.pos):
                    self.running = False
                    return "exit"

                # If game is completed, don't process further clicks
                if self.game_completed:
                    return None

                # Reset idle timer on click
                self.last_activity_time = time.time()

                # Check if clicked on a toy
                clicked_anything = False
                for i, toy in enumerate(self.toys):
                    if not toy["collected"] and toy["rect"].collidepoint(event.pos):
                        clicked_anything = True
                        # Mark as collected
                        toy["collected"] = True

                        # Add to collected items
                        self.collected_items.append(toy.copy())

                        # Show success message
                        self.show_message(f"You got the {toy['name']}! Keep it up!")

                        # Check if all toys are collected
                        if len(self.get_uncollected_toys()) == 0:
                            self.game_completed = True
                            self.show_congrats = True
                            self.congrats_timer = 180  # Show for 3 seconds at 60 FPS
                        break

                if not clicked_anything:
                    self.show_message("Go on! You can do it!")

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
                return "exit"

        return None

    # ======================================================
    # UPDATE
    # ======================================================
    def update(self):
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1

        # Update congrats timer
        if self.congrats_timer > 0:
            self.congrats_timer -= 1
        else:
            self.show_congrats = False

        # Check for idle movement (only if game not completed)
        if not self.game_completed:
            if time.time() - self.last_activity_time > self.idle_timer:
                if self.moving_object_index is None and self.get_uncollected_toys():
                    self.start_idle_movement()

            # Update idle movement
            self.update_idle_movement()

    # ======================================================
    # DRAWING
    # ======================================================
    def draw_toy(self, toy, screen_pos=None):
        """Draw toy image - removed hover effect"""
        if toy["collected"]:
            return

        rect = screen_pos if screen_pos else toy["rect"]
        img_key = toy["image"]

        if img_key in self.toy_images:
            img = self.toy_images[img_key]
            scaled_img = pygame.transform.scale(img, (rect.width, rect.height))
            self.screen.blit(scaled_img, rect)
        else:
            # Fallback
            color = self.GRAY
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2, border_radius=8)

    def draw_collected_items(self):
        """Draw the collected items section with all toys visible and checkmarks when collected"""
        # Draw section background
        section_surf = pygame.Surface((self.collected_area_rect.width, self.collected_area_rect.height),
                                      pygame.SRCALPHA)
        section_surf.fill((50, 50, 50, 180))
        self.screen.blit(section_surf, self.collected_area_rect)

        # Draw border
        pygame.draw.rect(self.screen, self.GOLD, self.collected_area_rect, 3, border_radius=10)

        # Draw title - changed from "Collected:" to "To Collect"
        title = self.small_font.render("To Collect", True, self.WHITE)
        title_rect = title.get_rect(centerx=self.collected_area_rect.centerx,
                                    top=self.collected_area_rect.top + 10)
        self.screen.blit(title, title_rect)

        # Draw all toys in the collection area with checkmarks if collected
        y_offset = self.collected_area_rect.top + 50
        for i, toy in enumerate(self.toys):
            if i * 40 > self.collected_area_rect.height - 60:
                break

            # Draw mini icon for every toy
            if toy["image"] in self.toy_images:
                img = self.toy_images[toy["image"]]
                mini_img = pygame.transform.scale(img, (30, 30))
                self.screen.blit(mini_img, (self.collected_area_rect.left + 10, y_offset))

            # Draw checkmark if collected
            if toy["collected"]:
                check = self.checkmark_font.render("✓", True, self.GREEN)
                self.screen.blit(check, (self.collected_area_rect.left + 45, y_offset - 5))

            # Draw name
            name = self.small_font.render(toy["name"], True, self.WHITE)
            self.screen.blit(name, (self.collected_area_rect.left + 50, y_offset + 5))

            y_offset += 40

    def draw_message(self):
        """Draw popup message"""
        if self.message_timer > 0 and self.message:
            # Create message background
            msg_surf = self.message_font.render(self.message, True, self.WHITE)
            msg_rect = msg_surf.get_rect(center=(self.w // 2, 150))

            # Draw bubble
            bubble_rect = msg_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, self.BLACK, bubble_rect, border_radius=15)
            pygame.draw.rect(self.screen, self.GOLD, bubble_rect, 3, border_radius=15)

            # Draw text
            self.screen.blit(msg_surf, msg_rect)

    def draw_congratulations(self):
        """Draw congratulations message when all items are collected"""
        if self.show_congrats:
            # Create semi-transparent overlay
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            # Draw congratulations text
            congrats_text = self.congrats_font.render("CONGRATULATIONS!", True, self.GOLD)
            congrats_rect = congrats_text.get_rect(center=(self.w // 2, self.h // 2 - 50))
            self.screen.blit(congrats_text, congrats_rect)

            congrats_text2 = self.message_font.render("You found all the toys!", True, self.WHITE)
            congrats_rect2 = congrats_text2.get_rect(center=(self.w // 2, self.h // 2 + 20))
            self.screen.blit(congrats_text2, congrats_rect2)

            # Instruction to exit
            exit_text = self.small_font.render("Click EXIT to return to main menu", True, self.WHITE)
            exit_rect = exit_text.get_rect(center=(self.w // 2, self.h // 2 + 70))
            self.screen.blit(exit_text, exit_rect)

    def draw(self):
        # Draw background
        if self.use_bg:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(self.bg_color)

        # Draw ground line
        for x in range(0, self.w, 20):
            pygame.draw.line(self.screen, (200, 200, 200), (x, self.ground_y), (x + 10, self.ground_y), 2)

        # Draw TOYS FIRST (behind equipment)
        for toy in self.toys:
            self.draw_toy(toy)

        # Draw EQUIPMENT ON TOP
        for ph in self.placeholders:
            img_key = ph["image"]
            if img_key in self.equipment_images:
                img = self.equipment_images[img_key]
                scaled_img = pygame.transform.scale(img, (ph["rect"].width, ph["rect"].height))
                self.screen.blit(scaled_img, ph["rect"])
            else:
                surf = pygame.Surface((ph["rect"].width, ph["rect"].height), pygame.SRCALPHA)
                color = (100, 100, 100, 180)
                pygame.draw.rect(surf, color, (0, 0, ph["rect"].width, ph["rect"].height), border_radius=8)
                self.screen.blit(surf, ph["rect"])

        # Draw collected items section
        self.draw_collected_items()

        # Draw message popup
        self.draw_message()

        # Draw title - CENTERED
        title = self.title_font.render("Find the Hidden Toys", True, self.BLACK)
        title_rect = title.get_rect(center=(self.w // 2, 40))
        self.screen.blit(title, title_rect)

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

        # Draw instruction (only if game not completed)
        if not self.game_completed:
            remaining = len(self.get_uncollected_toys())
            inst = self.small_font.render(f"Click on toys to collect them! ({remaining} remaining)", True, self.BLACK)
            self.screen.blit(inst, (40, 80))

        # Draw congratulations overlay if game completed
        self.draw_congratulations()

        pygame.display.flip()
        self.clock.tick(self.FPS)
        return self.running