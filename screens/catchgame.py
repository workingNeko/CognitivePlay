import pygame
import random
import time
import os

# Try to import moviepy – if not installed, skip tutorial gracefully
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("moviepy not installed – video tutorial will be skipped")


class CatchGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        # ---------- Load background ----------
        bg_path = os.path.join("assets", "images", "menu_background.png")
        self.bg_image = pygame.image.load(bg_path).convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (self.width, self.height))

        # ---------- Video tutorial with margins ----------
        self.state = "tutorial"           # "tutorial" -> "question" -> "game"
        self.video_path = os.path.join("assets", "videos", "catchgametutorial.mp4")
        self.video_clip = None
        self.video_frame_iter = None
        self.video_last_time = 0
        self.video_frame_duration = 1 / 30
        self.current_video_frame = None

        # Margins for video (2 inches ≈ 150 pixels on 96 DPI)
        self.video_margin = 150
        self.video_display_width = self.width - 2 * self.video_margin
        self.video_display_height = self.height - 2 * self.video_margin

        # Skip button (top‑right corner)
        self.skip_button = pygame.Rect(self.width - 150, 30, 120, 50)

        # Try to load the video
        if MOVIEPY_AVAILABLE and os.path.exists(self.video_path):
            try:
                self.video_clip = VideoFileClip(self.video_path)
                self.video_frame_duration = 1 / self.video_clip.fps
                self.video_frame_iter = self.video_clip.iter_frames(fps=self.video_clip.fps, dtype="uint8")
                self._video_next_frame()
                self.video_last_time = time.time()
            except Exception as e:
                print(f"Could not load video: {e}")
                self.skip_tutorial()
        else:
            if not MOVIEPY_AVAILABLE:
                print("moviepy not installed – skipping video tutorial")
            else:
                print("Video file not found – skipping tutorial")
            self.skip_tutorial()

        # ---------- Stop any previous music ----------
        pygame.mixer.music.stop()

        # ---------- Game background music (for actual game) ----------
        self.catchgame_music = os.path.join("assets", "sounds", "catchgamesound.wav")

        # ---------- Sound effects ----------
        self.bomb_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "bomb.mp3"))
        self.drop_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "drop.mp3"))
        self.drop_shape = pygame.mixer.Sound(os.path.join("assets", "sounds", "notcatched.mp3"))
        self.gameover_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "gameover.mp3"))
        self.gameover_played = False

        # ---------- Exit button ----------
        exit_path = os.path.join("assets", "images", "exitbutton.png")
        self.exit_image = pygame.image.load(exit_path).convert_alpha()
        self.exit_image = pygame.transform.scale(self.exit_image, (120, 60))
        self.exit_button = pygame.Rect(20, 20, 120, 60)

        # ---------- Fonts & colors ----------
        self.title_font = pygame.font.SysFont("Comic Sans MS", 52, bold=True)
        self.font = pygame.font.SysFont("Comic Sans MS", 30, bold=True)
        self.small_font = pygame.font.SysFont("Comic Sans MS", 22, bold=True)

        self.TEXT = (60, 60, 120)
        self.RED = (220, 70, 70)
        self.GREEN = (80, 200, 120)
        self.BLUE = (80, 130, 255)
        self.YELLOW = (255, 210, 90)
        self.PINK = (255, 150, 200)

        self.choice_colors = {
            "green": (80, 200, 120),
            "blue": (80, 130, 255),
            "yellow": (255, 210, 90),
            "pink": (255, 192, 203),
        }

        # ---------- Basket ----------
        basket_path = os.path.join("assets", "images", "basket.png")
        self.basket_img = pygame.image.load(basket_path).convert_alpha()
        self.basket_width, self.basket_height = 300, 80
        self.basket_img = pygame.transform.scale(self.basket_img, (self.basket_width, self.basket_height))
        self.basket = pygame.Rect(self.width // 2 - self.basket_width // 2,
                                  self.height - self.basket_height,
                                  self.basket_width, self.basket_height)
        self.basket_speed = 12

        # ---------- Bomb animation ----------
        self.bomb_frames = []
        for i in range(1, 4):
            path = os.path.join("assets", "images", f"bomb{i}.png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (48, 48))
            self.bomb_frames.append(img)
        self.bomb_frame_index = 0
        self.bomb_anim_speed = 0.2

        # ---------- Explosion animation ----------
        self.explosion_frames = []
        for i in range(1, 5):
            path = os.path.join("assets", "images", f"bombexplosion{i}.png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (150, 150))
            self.explosion_frames.append(img)
        self.active_explosions = []

        # ---------- Shape images ----------
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
        self.shape_size = 80
        for shape in self.shape_images:
            self.shape_images[shape] = [
                pygame.transform.scale(img, (self.shape_size, self.shape_size))
                for img in self.shape_images[shape]
            ]

        # ---------- Hearts ----------
        heart1_path = os.path.join("assets", "images", "heart1.png")
        heart2_path = os.path.join("assets", "images", "heart2.png")
        self.heart_images = {
            "normal": pygame.image.load(heart1_path).convert_alpha(),
            "damaged": pygame.image.load(heart2_path).convert_alpha()
        }
        heart_size = 30
        for key in self.heart_images:
            self.heart_images[key] = pygame.transform.scale(self.heart_images[key], (heart_size, heart_size))

        # ---------- Question data ----------
        self.questions = [
            {"shape": "square", "correct": "green", "choices": ["green", "blue"]},
            {"shape": "triangle", "correct": "yellow", "choices": ["yellow", "pink"]},
            {"shape": "circle", "correct": "blue", "choices": ["blue", "green"]}
        ]
        random.shuffle(self.questions)
        self.current_question = 0

        # ---------- Reset game variables ----------
        self.reset_game()

    # ---------- Video helpers ----------
    def _video_next_frame(self):
        """Fetch the next frame from the video iterator."""
        if not self.video_frame_iter:
            return
        try:
            frame = next(self.video_frame_iter)
            frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            self.current_video_frame = frame
        except StopIteration:
            self.skip_tutorial()
        except Exception as e:
            print(f"Video frame error: {e}")
            self.skip_tutorial()

    def skip_tutorial(self):
        """Exit tutorial mode and go to question mode."""
        if self.state == "tutorial":
            self.state = "question"
            if self.video_clip:
                self.video_clip.close()
                self.video_clip = None
            self.current_video_frame = None

    def draw_tutorial(self):
        """Draw the video frame with margins and the skip button."""
        # Draw full-screen background
        self.screen.blit(self.bg_image, (0, 0))

        # Draw video frame scaled to fit within margins
        if self.current_video_frame:
            scaled = pygame.transform.scale(self.current_video_frame,
                                            (self.video_display_width, self.video_display_height))
            self.screen.blit(scaled, (self.video_margin, self.video_margin))
        else:
            # Placeholder when video not loaded
            placeholder = self.font.render("VIDEO TUTORIAL (PLACEHOLDER)", True, self.TEXT)
            px = self.width // 2 - placeholder.get_width() // 2
            py = self.height // 2
            self.screen.blit(placeholder, (px, py))

        # Draw skip button
        mouse_pos = pygame.mouse.get_pos()
        btn_color = (100, 100, 200) if self.skip_button.collidepoint(mouse_pos) else (70, 70, 150)
        pygame.draw.rect(self.screen, btn_color, self.skip_button, border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), self.skip_button, 2, border_radius=10)
        skip_text = self.font.render("SKIP", True, (255, 255, 255))
        self.screen.blit(skip_text, skip_text.get_rect(center=self.skip_button.center))

    def update_tutorial(self):
        if not self.video_frame_iter:
            return
        now = time.time()
        if now - self.video_last_time >= self.video_frame_duration:
            self.video_last_time = now
            self._video_next_frame()

    # ---------- Question mode (unchanged, full screen) ----------
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
        mouse_pos = pygame.mouse.get_pos()
        choice1 = q["choices"][0]
        choice2 = q["choices"][1]
        color1 = self.choice_colors.get(choice1, (200, 200, 255))
        color2 = self.choice_colors.get(choice2, (200, 200, 255))

        def darken(c):
            return (max(c[0]-40, 0), max(c[1]-40, 0), max(c[2]-40, 0))

        if rect1.collidepoint(mouse_pos):
            color1 = darken(color1)
        if rect2.collidepoint(mouse_pos):
            color2 = darken(color2)

        pygame.draw.rect(self.screen, color1, rect1, border_radius=10)
        pygame.draw.rect(self.screen, color2, rect2, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), rect1, 3, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), rect2, 3, border_radius=10)

        c1_text = self.font.render(choice1, True, (0, 0, 0))
        c2_text = self.font.render(choice2, True, (0, 0, 0))
        self.screen.blit(c1_text, c1_text.get_rect(center=rect1.center))
        self.screen.blit(c2_text, c2_text.get_rect(center=rect2.center))

    def check_answer(self, answer):
        q = self.questions[self.current_question]
        if answer == q["correct"]:
            self.current_question += 1
            if self.current_question >= len(self.questions):
                self.state = "game"
                pygame.mixer.music.load(self.catchgame_music)
                pygame.mixer.music.play(-1)

    # ---------- Game logic (full screen, unchanged) ----------
    def reset_game(self):
        self.lives = 5
        self.score = 0
        self.spawn_delay = 2.0
        self.last_spawn = time.time()
        self.objects = []
        self.game_over = False
        self.win = False
        self.gameover_played = False
        self.targets = {
            "circle": 5,
            "square": 5,
            "triangle": 5
        }
        self.heart_blinks = {}

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

    def all_done(self):
        return all(count == 0 for count in self.targets.values())

    def update_game(self):
        if self.game_over or self.win:
            return

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

        self.bomb_frame_index += self.bomb_anim_speed
        if self.bomb_frame_index >= len(self.bomb_frames):
            self.bomb_frame_index = 0

        for obj in self.objects[:]:
            obj["y"] += obj["speed"]

            if obj["type"] in self.shape_images:
                now = time.time()
                if now - obj["last_frame_time"] >= obj["frame_delay"]:
                    obj["frame_index"] += 1
                    if obj["frame_index"] >= len(self.shape_images[obj["type"]]):
                        obj["frame_index"] = 0
                    obj["last_frame_time"] = now

            rect = pygame.Rect(obj["x"] - self.shape_size//2,
                               obj["y"] - self.shape_size//2,
                               self.shape_size, self.shape_size)

            if rect.colliderect(self.basket):
                if obj["type"] == "bomb":
                    self.bomb_sound.play()
                    heart_index = self.lives - 1
                    if heart_index >= 0:
                        self.heart_blinks[heart_index] = {
                            "start_time": time.time(),
                            "active": True,
                            "permanent_remove": False
                        }
                    self.active_explosions.append({
                        "x": self.basket.centerx,
                        "y": self.basket.centery,
                        "frame": 0,
                        "last_update": time.time()
                    })
                else:
                    self.drop_sound.play()
                    self.score += 10
                    if self.targets[obj["type"]] > 0:
                        self.targets[obj["type"]] -= 1
                self.objects.remove(obj)
                if self.all_done():
                    self.win = True

            elif obj["y"] > self.height:
                if obj["type"] != "bomb":
                    self.drop_shape.play()
                    heart_index = self.lives - 1
                    if heart_index >= 0:
                        self.heart_blinks[heart_index] = {
                            "start_time": time.time(),
                            "active": True,
                            "permanent_remove": False
                        }
                self.objects.remove(obj)

        for exp in self.active_explosions[:]:
            if time.time() - exp["last_update"] > 0.08:
                exp["frame"] += 1
                exp["last_update"] = time.time()
            if exp["frame"] >= len(self.explosion_frames):
                self.active_explosions.remove(exp)

        now = time.time()
        hearts_to_remove = []
        for hidx, blink in self.heart_blinks.items():
            if blink["active"]:
                if now - blink["start_time"] >= 0.8:
                    blink["permanent_remove"] = True
                    blink["active"] = False
                    self.lives -= 1
                    if self.lives <= 0 and not self.gameover_played:
                        self.gameover_sound.play()
                        self.gameover_played = True
                        self.game_over = True
                else:
                    blink["state"] = (int((now - blink["start_time"]) / 0.2) % 2 == 0)
            if blink.get("permanent_remove"):
                hearts_to_remove.append(hidx)
        for hidx in hearts_to_remove:
            del self.heart_blinks[hidx]

    def draw_game(self):
        self.screen.blit(self.bg_image, (0, 0))

        title = self.title_font.render("Catch the Shapes!", True, self.TEXT)
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 30))
        self.screen.blit(self.basket_img, self.basket.topleft)

        for obj in self.objects:
            if obj["type"] in self.shape_images:
                idx = int(obj["frame_index"])
                img = self.shape_images[obj["type"]][idx]
                rect = img.get_rect(center=(obj["x"], obj["y"]))
                self.screen.blit(img, rect)
            elif obj["type"] == "bomb":
                frame = self.bomb_frames[int(self.bomb_frame_index)]
                self.screen.blit(frame, (obj["x"]-24, obj["y"]-24))

        for exp in self.active_explosions:
            frame = self.explosion_frames[exp["frame"]]
            rect = frame.get_rect(center=(exp["x"], exp["y"]))
            self.screen.blit(frame, rect)

        heart_w = self.heart_images["normal"].get_width()
        total_hearts = self.lives
        for i in range(total_hearts):
            x_pos = 40 + i * (heart_w + 5)
            y_pos = 160
            if i in self.heart_blinks and self.heart_blinks[i]["active"]:
                if self.heart_blinks[i]["state"]:
                    self.screen.blit(self.heart_images["normal"], (x_pos, y_pos))
                else:
                    self.screen.blit(self.heart_images["damaged"], (x_pos, y_pos))
            else:
                self.screen.blit(self.heart_images["normal"], (x_pos, y_pos))

        score_txt = self.font.render(f"Score: {self.score}", True, self.TEXT)
        self.screen.blit(score_txt, (self.width - 250, 150))
        remaining = self.small_font.render(
            f"Left C:{self.targets['circle']} S:{self.targets['square']} T:{self.targets['triangle']}",
            True, self.TEXT)
        self.screen.blit(remaining, (self.width - 250, 200))

        self.screen.blit(self.exit_image, self.exit_button)

        if self.game_over:
            self.draw_end_screen("Game Over!", self.RED)
        if self.win:
            self.draw_end_screen("Congratulations! You did well!", self.GREEN)

    def draw_end_screen(self, text, color):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        msg = self.title_font.render(text, True, color)
        self.screen.blit(msg, (self.width//2 - msg.get_width()//2, self.height//2 - 50))
        hint = self.small_font.render("Press EXIT to return to Menu", True, (255, 255, 255))
        self.screen.blit(hint, (self.width//2 - hint.get_width()//2, self.height//2 + 20))

    # ---------- Master event handling & update loop ----------
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.exit_button.collidepoint(event.pos):
            pygame.mixer.music.stop()
            return "back"

        if self.state == "tutorial":
            if event.type == pygame.MOUSEBUTTONDOWN and self.skip_button.collidepoint(event.pos):
                self.skip_tutorial()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self.skip_tutorial()

        elif self.state == "question":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                q = self.questions[self.current_question]
                rect1 = pygame.Rect(self.width//2 - 200, 400, 150, 60)
                rect2 = pygame.Rect(self.width//2 + 50, 400, 150, 60)
                if rect1.collidepoint(mx, my):
                    self.check_answer(q["choices"][0])
                if rect2.collidepoint(mx, my):
                    self.check_answer(q["choices"][1])

        elif self.state == "game":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset_game()
                self.state = "game"
                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.catchgame_music)
                pygame.mixer.music.play(-1)

    def update(self):
        if self.state == "tutorial":
            self.update_tutorial()
        elif self.state == "question":
            pass
        elif self.state == "game":
            self.update_game()

    def draw(self):
        if self.state == "tutorial":
            self.draw_tutorial()
        elif self.state == "question":
            self.draw_question_screen()
        elif self.state == "game":
            self.draw_game()