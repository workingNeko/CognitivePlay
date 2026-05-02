import pygame
import random
import time
import os
import subprocess
import sys
import zipfile
import urllib.request
import platform


# ---------- Auto-install FFmpeg and deno ----------
def download_file(url, dest):
    """Download a file with progress reporting"""
    print(f"Downloading {os.path.basename(dest)}...")
    urllib.request.urlretrieve(url, dest)
    print("Download complete!")


def install_ffmpeg_windows():
    """Download and install FFmpeg on Windows"""
    ffmpeg_path = os.path.join(os.path.expanduser("~"), "ffmpeg")
    ffmpeg_bin = os.path.join(ffmpeg_path, "bin", "ffmpeg.exe")

    # Check if already installed
    if os.path.exists(ffmpeg_bin):
        # Add to PATH if not already there
        if ffmpeg_path not in os.environ.get("PATH", ""):
            os.environ["PATH"] += os.pathsep + os.path.join(ffmpeg_path, "bin")
        return True

    try:
        print("FFmpeg not found. Downloading...")
        # Download FFmpeg
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = os.path.join(os.path.expanduser("~"), "ffmpeg.zip")

        download_file(ffmpeg_url, zip_path)

        # Extract
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.expanduser("~"))

        # Rename the extracted folder
        extracted_folder = None
        for item in os.listdir(os.path.expanduser("~")):
            if item.startswith("ffmpeg-") and os.path.isdir(os.path.join(os.path.expanduser("~"), item)):
                extracted_folder = os.path.join(os.path.expanduser("~"), item)
                break

        if extracted_folder:
            # Move to ffmpeg folder
            if os.path.exists(ffmpeg_path):
                import shutil
                shutil.rmtree(ffmpeg_path)
            os.rename(extracted_folder, ffmpeg_path)

        # Clean up
        os.remove(zip_path)

        # Add to PATH
        os.environ["PATH"] += os.pathsep + os.path.join(ffmpeg_path, "bin")
        print(f"FFmpeg installed to {ffmpeg_path}")
        return True
    except Exception as e:
        print(f"Could not auto-install FFmpeg: {e}")
        print("Please manually install FFmpeg from: https://ffmpeg.org/download.html")
        return False


def ensure_deno_installed():
    """Install deno automatically if not present"""
    try:
        # Check if deno is already installed
        result = subprocess.run(['deno', '--version'], capture_output=True, check=False)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # Try to install deno
    system = platform.system()
    try:
        if system == "Windows":
            print("Deno not found. Installing via winget...")
            subprocess.run(['winget', 'install', 'Deno.Land.Deno', '--silent'],
                           capture_output=True, check=False)
        elif system == "Linux" or system == "Darwin":  # Darwin = macOS
            print("Deno not found. Installing via shell script...")
            install_cmd = 'curl -fsSL https://deno.land/install.sh | sh'
            subprocess.run(install_cmd, shell=True, capture_output=True, check=False)

        print("Deno installed. Please restart your game for changes to take effect.")
        return False
    except Exception as e:
        print(f"Could not auto-install deno: {e}")
        return True


# Install FFmpeg and deno
print("Checking for required dependencies...")
FFMPEG_INSTALLED = install_ffmpeg_windows()
DENO_INSTALLED = ensure_deno_installed()

if not FFMPEG_INSTALLED:
    print("WARNING: FFmpeg not available. Video playback may fail.")
    print("Please install FFmpeg manually from: https://ffmpeg.org/download.html")

# ---------- Try to import pyvidplayer2 for YouTube streaming ----------
try:
    from pyvidplayer2 import Video

    PYPVIDEO_AVAILABLE = True
except ImportError:
    PYPVIDEO_AVAILABLE = False
    print("pyvidplayer2 not installed – video tutorial will be skipped")
    print("Install with: pip install pyvidplayer2 yt-dlp")

# ---------- Fix for Pillow 10+ ----------
import PIL.Image

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS


class CatchGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        # ---------- Load background ----------
        bg_path = os.path.join("assets", "images", "menu_background.png")
        self.bg_image = pygame.image.load(bg_path).convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (self.width, self.height))

        # ---------- YouTube video tutorial ----------
        self.state = "tutorial"  # "tutorial" -> "question" -> "game"
        # 🔽 REPLACE THIS URL WITH YOUR ACTUAL YOUTUBE VIDEO URL
        self.youtube_url = "https://www.youtube.com/watch?v=GBIIQ0kP15E"
        self.video = None  # will be set if pyvidplayer2 works
        self.loading_video = False
        self.video_error = False  # track if video failed to load

        # Margins for video (2 inches ≈ 150 pixels on 96 DPI)
        self.video_margin = 150
        self.video_display_width = self.width - 2 * self.video_margin
        self.video_display_height = self.height - 2 * self.video_margin

        # Skip button (top‑right corner)
        self.skip_button = pygame.Rect(self.width - 150, 30, 120, 50)

        # ---------- Fade effect for smooth entry ----------
        self.tutorial_fade_active = True
        self.tutorial_fade_alpha = 255
        self.tutorial_fade_start_time = time.time()
        self.tutorial_fade_duration = 2.0  # 2 seconds fade from black

        # ---------- Try to load YouTube video ----------
        if PYPVIDEO_AVAILABLE and not self.video_error:
            try:
                self.loading_video = True
                print("Loading YouTube video...")
                # Create video object from YouTube URL
                self.video = Video(self.youtube_url, youtube=True)
                # Set volume (0.0 to 1.0)
                self.video.set_volume(0.8)
                self.loading_video = False
                self.tutorial_start_time = time.time()
                print("YouTube video loaded – ready to play")
            except Exception as e:
                print(f"Could not load YouTube video: {e}")
                self.video_error = True
                self.skip_tutorial()
        else:
            if not PYPVIDEO_AVAILABLE:
                print("pyvidplayer2 missing – skipping tutorial")
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
    def skip_tutorial(self):
        """Exit tutorial mode and go to question mode."""
        if self.state == "tutorial":
            self.state = "question"
            # Stop and close video if it exists
            if self.video:
                try:
                    self.video.stop()
                except:
                    pass
                self.video = None
            self.loading_video = False

    def draw_tutorial(self):
        """Draw the YouTube video frame with margins, skip button, fade overlay, and a border."""
        self.screen.blit(self.bg_image, (0, 0))

        # If still loading, show message
        if self.loading_video:
            load_text = self.font.render("Loading YouTube video...", True, (255, 255, 255))
            self.screen.blit(load_text, (self.width // 2 - load_text.get_width() // 2,
                                         self.height // 2))
        # Otherwise draw current video frame (scaled to margins)
        elif self.video and not self.video_error:
            try:
                # Access the current frame as an attribute
                if hasattr(self.video, 'frame_surf'):
                    frame_surf = self.video.frame_surf
                else:
                    frame_surf = None

                if frame_surf is not None:
                    # Scale to fit the display area
                    scaled = pygame.transform.scale(frame_surf,
                                                    (self.video_display_width, self.video_display_height))
                    self.screen.blit(scaled, (self.video_margin, self.video_margin))
                else:
                    # No frame yet (buffering)
                    buffer_text = self.font.render("Buffering...", True, (255, 255, 255))
                    self.screen.blit(buffer_text, (self.width // 2 - buffer_text.get_width() // 2,
                                                   self.height // 2))
            except Exception as e:
                print(f"Error drawing video: {e}")
                self.video_error = True
        else:
            # Placeholder when no video loaded
            placeholder = self.font.render("VIDEO TUTORIAL NOT AVAILABLE", True, self.TEXT)
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

        # --- DRAW THE VIDEO FRAME BORDER ---
        border_rect = pygame.Rect(self.video_margin, self.video_margin,
                                  self.video_display_width, self.video_display_height)
        pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 3, border_radius=10)

        # Fade overlay only after loading
        if not self.loading_video and not self.video_error and self.tutorial_fade_active:
            fade_surface = pygame.Surface((self.width, self.height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.tutorial_fade_alpha)
            self.screen.blit(fade_surface, (0, 0))

    def update_tutorial(self):
        """Update the tutorial video playback."""
        # Update video playback
        if self.loading_video or self.video_error or not self.video:
            return

        try:
            # Tell the video to update (advance time, fetch new frames)
            self.video.update()

            # Check if video is still playing (using active attribute)
            if hasattr(self.video, 'active') and not self.video.active:
                self.skip_tutorial()
                return
        except Exception as e:
            print(f"Video update error: {e}")
            self.video_error = True
            self.skip_tutorial()
            return

        # Update fade effect
        if self.tutorial_fade_active:
            now = time.time()
            elapsed = now - self.tutorial_fade_start_time
            if elapsed >= self.tutorial_fade_duration:
                self.tutorial_fade_active = False
                self.tutorial_fade_alpha = 0
            else:
                self.tutorial_fade_alpha = int(255 * (1 - elapsed / self.tutorial_fade_duration))

    # ---------- Question mode (unchanged) ----------
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
            return (max(c[0] - 40, 0), max(c[1] - 40, 0), max(c[2] - 40, 0))

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
            self.drop_sound.play()
            self.current_question += 1
            if self.current_question >= len(self.questions):
                self.state = "game"
                pygame.mixer.music.load(self.catchgame_music)
                pygame.mixer.music.play(-1)
        else:
            self.drop_shape.play()

    # ---------- Game logic (unchanged) ----------
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

            rect = pygame.Rect(obj["x"] - self.shape_size // 2,
                               obj["y"] - self.shape_size // 2,
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
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 30))
        self.screen.blit(self.basket_img, self.basket.topleft)

        for obj in self.objects:
            if obj["type"] in self.shape_images:
                idx = int(obj["frame_index"])
                img = self.shape_images[obj["type"]][idx]
                rect = img.get_rect(center=(obj["x"], obj["y"]))
                self.screen.blit(img, rect)
            elif obj["type"] == "bomb":
                frame = self.bomb_frames[int(self.bomb_frame_index)]
                self.screen.blit(frame, (obj["x"] - 24, obj["y"] - 24))

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
        self.screen.blit(msg, (self.width // 2 - msg.get_width() // 2, self.height // 2 - 50))
        hint = self.small_font.render("Press EXIT to return to Menu", True, (255, 255, 255))
        self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height // 2 + 20))

    # ---------- Master event handling & update loop ----------
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.exit_button.collidepoint(event.pos):
            pygame.mixer.music.stop()
            if self.video:
                try:
                    self.video.stop()
                except:
                    pass
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
                rect1 = pygame.Rect(self.width // 2 - 200, 400, 150, 60)
                rect2 = pygame.Rect(self.width // 2 + 50, 400, 150, 60)
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