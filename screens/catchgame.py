import pygame
import random
import time
import os


class CatchGame:

    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        # Background
        bg_path = os.path.join("assets", "images", "menu_background.png")
        self.bg_image = pygame.image.load(bg_path).convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (self.width, self.height))

        # Exit button
        exit_path = os.path.join("assets", "images", "exitbutton.png")
        self.exit_image = pygame.image.load(exit_path).convert_alpha()
        self.exit_image = pygame.transform.scale(self.exit_image, (120, 60))
        self.exit_button = pygame.Rect(20, 20, 120, 60)

        # Fonts
        self.title_font = pygame.font.SysFont("Comic Sans MS", 52, bold=True)
        self.font = pygame.font.SysFont("Comic Sans MS", 30, bold=True)
        self.small_font = pygame.font.SysFont("Comic Sans MS", 22, bold=True)

        # Colors
        self.TEXT = (60, 60, 120)
        self.RED = (220, 70, 70)
        self.GREEN = (80, 200, 120)
        self.BLUE = (80, 130, 255)
        self.YELLOW = (255, 210, 90)
        self.PINK = (255, 150, 200)

        # Basket
        self.basket = pygame.Rect(self.width // 2 - 150, self.height - 80, 300, 30)
        self.basket_speed = 12

        # Bomb animation
        self.bomb_frames = []
        for i in range(1, 4):
            path = os.path.join("assets", "images", f"bomb{i}.png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (48, 48))
            self.bomb_frames.append(img)
        self.bomb_frame_index = 0
        self.bomb_anim_speed = 0.2

        # Bomb explosion animation (YOU ALREADY HAD THIS)
        self.explosion_frames = []
        for i in range(1, 5):
            path = os.path.join("assets", "images", f"bombexplosion{i}.png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (150, 150))
            self.explosion_frames.append(img)

        self.active_explosions = []

        # Shape images
        self.shape_images = {
            "square": [
                pygame.image.load(os.path.join("assets", "images", "square1.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "images", "square2.png")).convert_alpha()
            ],
            "circle": [
                pygame.image.load(os.path.join("assets", "images", "circle1.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "images", "circle2.png")).convert_alpha()
            ],
            "triangle": [
                pygame.image.load(os.path.join("assets", "images", "triangle1.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "images", "triangle2.png")).convert_alpha()
            ]
        }

        # Heart images
        heart1_path = os.path.join("assets", "images", "heart1.png")
        heart2_path = os.path.join("assets", "images", "heart2.png")
        self.heart_images = {
            "normal": pygame.image.load(heart1_path).convert_alpha(),
            "damaged": pygame.image.load(heart2_path).convert_alpha()
        }

        # Scale hearts
        heart_size = 30
        for key in self.heart_images:
            self.heart_images[key] = pygame.transform.scale(self.heart_images[key], (heart_size, heart_size))

        # Basket
        basket_path = os.path.join("assets", "images", "basket.png")
        self.basket_img = pygame.image.load(basket_path).convert_alpha()
        self.basket_width, self.basket_height = 300, 80
        self.basket_img = pygame.transform.scale(self.basket_img, (self.basket_width, self.basket_height))
        self.basket = pygame.Rect(self.width // 2 - self.basket_width // 2, self.height - self.basket_height,
                                  self.basket_width, self.basket_height)
        self.basket_speed = 12

        # Scale all shapes to bigger size
        self.shape_size = 80
        for shape in self.shape_images:
            self.shape_images[shape] = [
                pygame.transform.scale(img, (self.shape_size, self.shape_size))
                for img in self.shape_images[shape]
            ]

        # QUESTION MODE
        self.question_mode = True
        self.current_question = 0
        self.questions = [
            {"shape": "square", "correct": "green", "choices": ["green", "blue"]},
            {"shape": "triangle", "correct": "yellow", "choices": ["yellow", "pink"]},
            {"shape": "circle", "correct": "blue", "choices": ["blue", "green"]}
        ]

        self.reset_game()

    # --------------------------------
    def reset_game(self):
        self.lives = 5
        self.score = 0
        self.spawn_delay = 1.5
        self.last_spawn = time.time()
        self.objects = []
        self.game_over = False
        self.win = False
        self.targets = {
            "circle": 5,
            "square": 5,
            "triangle": 5
        }

        # Heart blinking effects
        self.heart_blinks = {}  # Dictionary to track blinking hearts

    # --------------------------------
    def spawn_object(self):
        choices = [shape for shape, count in self.targets.items() if count > 0]
        choices.append("bomb")

        if not choices:
            return None

        obj_type = random.choice(choices)
        x = random.randint(50, self.width - 50)

        return {
            "type": obj_type,
            "x": x,
            "y": 0,
            "speed": random.randint(4, 7),
            "frame_index": 0,
            "last_frame_time": time.time(),
            "frame_delay": 0.5
        }

    # --------------------------------
    def handle_event(self, event):
        if self.question_mode:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                rect1 = pygame.Rect(self.width // 2 - 200, 400, 150, 60)
                rect2 = pygame.Rect(self.width // 2 + 50, 400, 150, 60)
                if rect1.collidepoint(mx, my):
                    self.check_answer(self.questions[self.current_question]["choices"][0])
                if rect2.collidepoint(mx, my):
                    self.check_answer(self.questions[self.current_question]["choices"][1])
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.exit_button.collidepoint(event.pos):
                return "back"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_game()
                self.question_mode = True
                self.current_question = 0

    # --------------------------------
    def check_answer(self, answer):
        correct = self.questions[self.current_question]["correct"]
        if answer == correct:
            self.current_question += 1
            if self.current_question >= len(self.questions):
                self.question_mode = False

    # --------------------------------
    def update(self):
        if self.question_mode or self.game_over or self.win:
            return

        self.bomb_frame_index += self.bomb_anim_speed
        if self.bomb_frame_index >= len(self.bomb_frames):
            self.bomb_frame_index = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.basket.x -= self.basket_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.basket.x += self.basket_speed
        self.basket.x = max(0, min(self.width - self.basket.width, self.basket.x))

        if time.time() - self.last_spawn >= self.spawn_delay:
            if not self.all_done():
                obj = self.spawn_object()
                if obj:
                    self.objects.append(obj)
                self.last_spawn = time.time()

        for obj in self.objects[:]:
            obj["y"] += obj["speed"]

            if obj["type"] in self.shape_images:
                now = time.time()
                if now - obj["last_frame_time"] >= obj["frame_delay"]:
                    obj["frame_index"] += 1
                    if obj["frame_index"] >= len(self.shape_images[obj["type"]]):
                        obj["frame_index"] = 0
                    obj["last_frame_time"] = now

            rect = pygame.Rect(obj["x"] - self.shape_size // 2,
                               obj["y"] - self.shape_size // 2,
                               self.shape_size, self.shape_size)

            if rect.colliderect(self.basket):
                if obj["type"] == "bomb":
                    # Start blinking effect for the heart that will be lost
                    heart_index = self.lives - 1  # The heart that will be lost
                    if heart_index >= 0 and heart_index < 5:
                        self.heart_blinks[heart_index] = {
                            "start_time": time.time(),
                            "active": True,
                            "permanent_remove": False  # Will be set to True after blinking
                        }

                    # Don't remove life immediately - wait for blink to finish
                    # EXPLOSION TRIGGER
                    self.active_explosions.append({
                        "x": self.basket.centerx,
                        "y": self.basket.centery,
                        "frame": 0,
                        "last_update": time.time()
                    })

                else:
                    self.score += 10
                    if self.targets[obj["type"]] > 0:
                        self.targets[obj["type"]] -= 1

                self.objects.remove(obj)

                if self.all_done():
                    self.win = True

            elif obj["y"] > self.height:
                if obj["type"] != "bomb":
                    # Start blinking effect for the heart that will be lost
                    heart_index = self.lives - 1
                    if heart_index >= 0 and heart_index < 5:
                        self.heart_blinks[heart_index] = {
                            "start_time": time.time(),
                            "active": True,
                            "permanent_remove": False
                        }

                self.objects.remove(obj)

        # UPDATE EXPLOSIONS
        for explosion in self.active_explosions[:]:
            if time.time() - explosion["last_update"] > 0.08:
                explosion["frame"] += 1
                explosion["last_update"] = time.time()

            if explosion["frame"] >= len(self.explosion_frames):
                self.active_explosions.remove(explosion)

        # UPDATE HEART BLINKS
        current_time = time.time()
        hearts_to_remove = []

        for heart_index, blink_data in self.heart_blinks.items():
            if blink_data["active"]:
                time_elapsed = current_time - blink_data["start_time"]

                # Blink for 0.8 seconds (2 blinks = on-off-on-off, each state 0.2 seconds)
                if time_elapsed >= 0.8:
                    # Blinking finished, mark for permanent removal
                    blink_data["permanent_remove"] = True
                    blink_data["active"] = False
                    self.lives -= 1  # Actually remove the life after blinking

                    if self.lives <= 0:
                        self.game_over = True
                else:
                    # Calculate blink state (True for heart1, False for heart2)
                    # Alternate every 0.2 seconds
                    blink_state = (int(time_elapsed / 0.2) % 2 == 0)
                    blink_data["state"] = blink_state

            # Check if this heart should be permanently removed
            if blink_data.get("permanent_remove", False):
                hearts_to_remove.append(heart_index)

        # Remove completed blink animations
        for heart_index in hearts_to_remove:
            del self.heart_blinks[heart_index]

    # --------------------------------
    def draw(self):
        if self.question_mode:
            self.draw_question_screen()
            return

        self.screen.blit(self.bg_image, (0, 0))
        title = self.title_font.render("Catch the Shapes!", True, self.TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 30))
        self.screen.blit(self.basket_img, self.basket.topleft)

        for obj in self.objects:
            self.draw_object(obj)

        # DRAW EXPLOSIONS
        for explosion in self.active_explosions:
            frame = self.explosion_frames[explosion["frame"]]
            rect = frame.get_rect(center=(explosion["x"], explosion["y"]))
            self.screen.blit(frame, rect)

        # Hearts - Draw all hearts including blinking ones
        heart_width = self.heart_images["normal"].get_width()

        # Calculate how many hearts to show (lives + blinking hearts that haven't been removed yet)
        total_hearts_to_draw = self.lives

        # Add any hearts that are blinking but haven't been permanently removed yet
        for heart_index in self.heart_blinks.keys():
            if heart_index >= total_hearts_to_draw:
                total_hearts_to_draw = heart_index + 1

        for i in range(total_hearts_to_draw):
            x_pos = 40 + i * (heart_width + 5)
            y_pos = 160

            # Check if this heart is blinking
            if i in self.heart_blinks and self.heart_blinks[i]["active"]:
                # Use heart1 or heart2 based on blink state
                if self.heart_blinks[i]["state"]:
                    self.screen.blit(self.heart_images["normal"], (x_pos, y_pos))
                else:
                    self.screen.blit(self.heart_images["damaged"], (x_pos, y_pos))
            elif i < self.lives:
                # Normal heart (not blinking and still alive)
                self.screen.blit(self.heart_images["normal"], (x_pos, y_pos))
            # If i >= self.lives, it's a blinking heart that will be removed soon

        score = self.font.render(f"Score: {self.score}", True, self.TEXT)
        self.screen.blit(score, (self.width - 250, 150))

        remaining = self.small_font.render(
            f"Left C:{self.targets['circle']} S:{self.targets['square']} T:{self.targets['triangle']}",
            True, self.TEXT)
        self.screen.blit(remaining, (self.width - 250, 200))
        self.screen.blit(self.exit_image, self.exit_button)

        if self.game_over:
            self.draw_end_screen("Game Over!", self.RED)
        if self.win:
            self.draw_end_screen("Congratulations! You did well!", self.GREEN)

    # --------------------------------
    def draw_question_screen(self):
        self.screen.blit(self.bg_image, (0, 0))
        q = self.questions[self.current_question]
        text = self.font.render(f"What color is the {q['shape']}?", True, self.TEXT)
        self.screen.blit(text, (self.width // 2 - text.get_width() // 2, 200))
        x, y = self.width // 2, 300

        img = self.shape_images[q["shape"]][0]
        rect = img.get_rect(center=(x, y))
        self.screen.blit(img, rect)

        rect1 = pygame.Rect(self.width // 2 - 200, 400, 150, 60)
        rect2 = pygame.Rect(self.width // 2 + 50, 400, 150, 60)
        pygame.draw.rect(self.screen, (200, 200, 255), rect1)
        pygame.draw.rect(self.screen, (200, 200, 255), rect2)

        c1 = self.font.render(q["choices"][0], True, self.TEXT)
        c2 = self.font.render(q["choices"][1], True, self.TEXT)
        self.screen.blit(c1, (rect1.x + 20, rect1.y + 15))
        self.screen.blit(c2, (rect2.x + 20, rect2.y + 15))

    # --------------------------------
    def draw_object(self, obj):
        x, y = obj["x"], obj["y"]
        if obj["type"] in self.shape_images:
            index = int(obj["frame_index"])
            img = self.shape_images[obj["type"]][index]
            rect = img.get_rect(center=(x, y))
            self.screen.blit(img, rect)
        elif obj["type"] == "bomb":
            frame = self.bomb_frames[int(self.bomb_frame_index)]
            self.screen.blit(frame, (x - 24, y - 24))

    # --------------------------------
    def draw_end_screen(self, text, color):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        msg = self.title_font.render(text, True, color)
        self.screen.blit(msg, (self.width // 2 - msg.get_width() // 2, self.height // 2 - 50))
        hint = self.small_font.render("Press EXIT to return to Menu", True, (255, 255, 255))
        self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height // 2 + 20))

    # --------------------------------
    def all_done(self):
        return all(count == 0 for count in self.targets.values())