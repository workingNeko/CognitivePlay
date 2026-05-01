# screens/minipuzzle.py
import pygame
import os
import random


class MiniPuzzleGame:
    def __init__(self, screen):
        self.screen = screen
        self.w, self.h = screen.get_size()

        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "preview"  # preview, playing, completed

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

        # Puzzle dimensions (2x2 = 4 pieces)
        self.rows = 2
        self.cols = 2
        self.total_pieces = self.rows * self.cols  # =4

        # Puzzle frame settings - CENTERED
        frame_width = 300   # 2 * 150
        frame_height = 300  # 2 * 150
        # Center the frame horizontally and vertically
        frame_x = (self.w - frame_width) // 2   # Shift left to make room for dashboard
        frame_y = (self.h - frame_height) // 2
        self.frame_rect = pygame.Rect(frame_x, frame_y, frame_width, frame_height)

        # Calculate piece dimensions
        self.piece_width = frame_width // self.cols  # 150
        self.piece_height = frame_height // self.rows  # 150

        # Dashboard area (right side) - LARGER to fit the 4 pieces
        dashboard_width = 380
        dashboard_height = 500
        self.dashboard_rect = pygame.Rect(
            self.frame_rect.right + 100,
            self.frame_rect.top - 30,
            dashboard_width,
            dashboard_height
        )

        # Drag and drop variables
        self.dragging_piece = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Message variables
        self.message = ""
        self.message_timer = 0
        self.message_duration = 120

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (30, 30, 30)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        self.GOLD = (255, 215, 0)
        self.GREEN = (34, 139, 34)
        self.BLUE = (100, 149, 237)

        # Load assets
        assets_path = os.path.join("assets", "images")

        # Load duck image
        self.duck_image = None
        self.piece_surfaces = []  # Store pre-rendered piece surfaces
        duck_path = os.path.join(assets_path, "duck.png")
        if os.path.exists(duck_path):
            try:
                self.duck_image = pygame.image.load(duck_path).convert_alpha()
                # Scale duck image to frame size
                scaled_duck = pygame.transform.scale(self.duck_image, (frame_width, frame_height))

                # Pre-render all pieces
                for row in range(self.rows):
                    for col in range(self.cols):
                        piece_surf = pygame.Surface((self.piece_width, self.piece_height), pygame.SRCALPHA)
                        src_x = col * self.piece_width
                        src_y = row * self.piece_height
                        piece_surf.blit(scaled_duck, (0, 0), (src_x, src_y, self.piece_width, self.piece_height))
                        self.piece_surfaces.append(piece_surf)

                print("Loaded duck image and pre-rendered pieces (4 pieces)")
            except Exception as e:
                print(f"Could not load duck image: {e}")

        # Load exit button image
        self.exit_button_img = None
        exit_img_path = os.path.join(assets_path, "exitbutton.png")
        if os.path.exists(exit_img_path):
            try:
                self.exit_button_img = pygame.image.load(exit_img_path).convert_alpha()
                self.exit_button_img = pygame.transform.scale(self.exit_button_img, (120, 60))
                print("Loaded exit button image")
            except Exception as e:
                print(f"Could not load exit button image: {e}")

        # Exit button
        if self.exit_button_img:
            self.exit_rect = self.exit_button_img.get_rect(topleft=(20, 20))
        else:
            self.exit_rect = pygame.Rect(20, 20, 120, 60)

        self.exit_hover = False

        # Fonts=
        self.title_font = pygame.font.SysFont("Comic Sans MS", 48, bold=True)
        self.large_font = pygame.font.SysFont("Comic Sans MS", 36, bold=True)
        self.medium_font = pygame.font.SysFont("Comic Sans MS", 24)
        self.small_font = pygame.font.SysFont("Comic Sans MS", 20)

        # Pre-render checkmark
        self.check_font = pygame.font.SysFont("Comic Sans MS", 30)
        self.checkmark = self.check_font.render("✓", True, self.GREEN)

        # Initialize puzzle pieces (will be shuffled when game starts)
        self.init_puzzle()

    def init_puzzle(self):
        """Initialize or reset the puzzle with pieces in order (for preview)"""
        # Create the correct pieces (in order)
        self.correct_pieces = []
        for row in range(self.rows):
            for col in range(self.cols):
                piece_rect = pygame.Rect(
                    self.frame_rect.x + col * self.piece_width,
                    self.frame_rect.y + row * self.piece_height,
                    self.piece_width,
                    self.piece_height
                )
                self.correct_pieces.append({
                    "correct_rect": piece_rect,
                    "row": row,
                    "col": col,
                    "index": row * self.cols + col
                })

        # For preview, keep pieces in order (not shuffled)
        self.preview_pieces = []
        for i, correct in enumerate(self.correct_pieces):
            piece = {
                "id": i,
                "original_index": i,
                "rect": correct["correct_rect"],  # Place in correct position for preview
                "correct_rect": correct["correct_rect"],
                "row": correct["row"],
                "col": correct["col"],
                "placed": False,
                "surface_idx": correct["index"],
                "preview": True
            }
            self.preview_pieces.append(piece)

        # Shuffled pieces (for playing)
        self.pieces = []

    def shuffle_pieces(self):
        """Shuffle the puzzle pieces for gameplay"""
        self.pieces = []
        positions = list(range(self.total_pieces))
        random.shuffle(positions)

        for i, pos_idx in enumerate(positions):
            correct = self.correct_pieces[pos_idx]

            # Position in dashboard area (right side) - 2 columns with spacing
            dashboard_x = self.dashboard_rect.x + 30 + (i % 2) * (self.piece_width + 20)
            dashboard_y = self.dashboard_rect.y + 60 + (i // 2) * (self.piece_height + 15)

            piece = {
                "id": i,
                "original_index": pos_idx,
                "rect": pygame.Rect(dashboard_x, dashboard_y, self.piece_width, self.piece_height),
                "correct_rect": correct["correct_rect"],
                "row": correct["row"],
                "col": correct["col"],
                "placed": False,
                "surface_idx": correct["index"]
            }
            self.pieces.append(piece)

    def start_game(self):
        """Start the game by shuffling pieces"""
        self.game_state = "playing"
        self.shuffle_pieces()
        self.show_message("Drag pieces to the frame!")

    def check_piece_placement(self, piece):
        """Check if a piece is in the correct position"""
        correct_rect = piece["correct_rect"]
        piece_center = piece["rect"].center
        correct_center = correct_rect.center

        distance = ((piece_center[0] - correct_center[0]) ** 2 +
                    (piece_center[1] - correct_center[1]) ** 2) ** 0.5

        return distance < 30

    def snap_to_correct(self, piece):
        """Snap piece to its correct position"""
        piece["rect"].x = piece["correct_rect"].x
        piece["rect"].y = piece["correct_rect"].y
        piece["placed"] = True

    def check_all_placed(self):
        """Check if all pieces are in correct positions"""
        for piece in self.pieces:
            if not piece["placed"]:
                return False
        return True

    def show_message(self, text):
        """Display a popup message"""
        self.message = text
        self.message_timer = self.message_duration

    # ======================================================
    # EVENTS
    # ======================================================
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.exit_hover = self.exit_rect.collidepoint(event.pos)

            # Handle dragging (only in playing state)
            if self.dragging_piece is not None and self.game_state == "playing":
                piece = self.pieces[self.dragging_piece]
                piece["rect"].x = event.pos[0] - self.drag_offset_x
                piece["rect"].y = event.pos[1] - self.drag_offset_y

                # Keep within screen bounds
                piece["rect"].x = max(0, min(self.w - piece["rect"].width, piece["rect"].x))
                piece["rect"].y = max(0, min(self.h - piece["rect"].height, piece["rect"].y))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check exit button
                if self.exit_rect.collidepoint(event.pos):
                    self.running = False
                    return "exit"

                if self.game_state == "preview":
                    # Check if clicked on "Play" area
                    play_rect = pygame.Rect(self.w // 2 - 100, self.frame_rect.bottom + 60, 200, 60)
                    if play_rect.collidepoint(event.pos):
                        self.start_game()

                elif self.game_state == "playing":
                    # Check for piece dragging (check in reverse for top pieces)
                    for i in range(len(self.pieces) - 1, -1, -1):
                        piece = self.pieces[i]
                        if not piece["placed"] and piece["rect"].collidepoint(event.pos):
                            self.dragging_piece = i
                            self.drag_offset_x = event.pos[0] - piece["rect"].x
                            self.drag_offset_y = event.pos[1] - piece["rect"].y
                            break

                elif self.game_state == "completed":
                    # Check if clicked on "Play Again" area
                    play_again_rect = pygame.Rect(self.w // 2 - 100, self.h // 2 + 100, 200, 60)
                    if play_again_rect.collidepoint(event.pos):
                        self.game_state = "preview"
                        self.init_puzzle()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_piece is not None and self.game_state == "playing":
                piece = self.pieces[self.dragging_piece]

                # Check if piece should snap to correct position
                if self.check_piece_placement(piece):
                    self.snap_to_correct(piece)

                    # Check if puzzle is complete
                    if self.check_all_placed():
                        self.game_state = "completed"
                        self.show_message("Congratulations! You solved the puzzle!")

                self.dragging_piece = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
                return "exit"

            # Press SPACE to start from preview
            if event.key == pygame.K_SPACE and self.game_state == "preview":
                self.start_game()

            # Press R to restart/shuffle (only in playing state)
            if event.key == pygame.K_r and self.game_state == "playing":
                self.shuffle_pieces()
                self.show_message("Puzzle shuffled!")

        return None

    # ======================================================
    # UPDATE
    # ======================================================
    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1

    # ======================================================
    # DRAWING
    # ======================================================
    def draw_piece(self, piece, is_preview=False):
        """Draw a puzzle piece"""
        if self.piece_surfaces and piece["surface_idx"] < len(self.piece_surfaces):
            # Use pre-rendered surface
            self.screen.blit(self.piece_surfaces[piece["surface_idx"]], piece["rect"])
            # Draw border
            pygame.draw.rect(self.screen, self.BLACK, piece["rect"], 2)

            # Draw checkmark on placed pieces (only in playing mode)
            if not is_preview and piece.get("placed", False):
                check_rect = self.checkmark.get_rect(center=piece["rect"].center)
                self.screen.blit(self.checkmark, check_rect)
        else:
            # Fallback if no duck image
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
            color = colors[piece["surface_idx"] % 4]
            pygame.draw.rect(self.screen, color, piece["rect"])
            pygame.draw.rect(self.screen, self.BLACK, piece["rect"], 2)

    def draw_preview_screen(self):
        """Draw the preview screen with completed puzzle"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Draw title
        title = self.large_font.render("Duck Puzzle", True, self.GOLD)
        title_rect = title.get_rect(center=(self.w // 2, 70))
        self.screen.blit(title, title_rect)

        # Draw instruction
        inst1 = self.medium_font.render("Press SPACE or Click PLAY to start", True, self.WHITE)
        inst1_rect = inst1.get_rect(center=(self.w // 2, self.frame_rect.bottom + 30))
        self.screen.blit(inst1, inst1_rect)

        # Draw play button
        play_rect = pygame.Rect(self.w // 2 - 100, self.frame_rect.bottom + 60, 200, 60)
        pygame.draw.rect(self.screen, self.GREEN, play_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.GOLD, play_rect, 3, border_radius=10)

        play_text = self.large_font.render("PLAY", True, self.WHITE)
        play_text_rect = play_text.get_rect(center=play_rect.center)
        self.screen.blit(play_text, play_text_rect)

        # Draw the completed puzzle in the frame (for preview)
        for piece in self.preview_pieces:
            self.draw_piece(piece, is_preview=True)

        # Draw frame border (highlight it)
        pygame.draw.rect(self.screen, self.GOLD, self.frame_rect, 4)

    def draw_playing_screen(self):
        """Draw the game screen while playing"""
        # Draw title
        title = self.medium_font.render("Duck Puzzle", True, self.GOLD)
        title_rect = title.get_rect(center=(self.w // 2, 40))
        self.screen.blit(title, title_rect)

        # Draw frame (empty grid)
        pygame.draw.rect(self.screen, self.WHITE, self.frame_rect, 3)

        # Draw grid lines
        for col in range(1, self.cols):
            x = self.frame_rect.x + col * self.piece_width
            pygame.draw.line(self.screen, self.WHITE, (x, self.frame_rect.y),
                             (x, self.frame_rect.bottom), 2)

        for row in range(1, self.rows):
            y = self.frame_rect.y + row * self.piece_height
            pygame.draw.line(self.screen, self.WHITE, (self.frame_rect.x, y),
                             (self.frame_rect.right, y), 2)

        # Draw dashboard background (right side)
        dashboard_surf = pygame.Surface((self.dashboard_rect.width, self.dashboard_rect.height), pygame.SRCALPHA)
        dashboard_surf.fill((50, 50, 50, 180))
        self.screen.blit(dashboard_surf, self.dashboard_rect)
        pygame.draw.rect(self.screen, self.GOLD, self.dashboard_rect, 3, border_radius=10)

        # Draw dashboard title
        dash_title = self.medium_font.render("Pieces to Place", True, self.WHITE)
        dash_title_rect = dash_title.get_rect(centerx=self.dashboard_rect.centerx, top=self.dashboard_rect.top + 10)
        self.screen.blit(dash_title, dash_title_rect)

        # Draw unplaced pieces in dashboard
        for piece in self.pieces:
            if not piece["placed"]:
                self.draw_piece(piece)

        # Draw placed pieces in frame
        for piece in self.pieces:
            if piece["placed"]:
                self.draw_piece(piece)

        # Draw instruction
        remaining = sum(1 for p in self.pieces if not p["placed"])
        if remaining == 0:
            inst = self.medium_font.render("PUZZLE COMPLETE!", True, self.GOLD)
        else:
            inst = self.small_font.render(f"Place all pieces! ({remaining} remaining) - Press R to shuffle", True,
                                          self.WHITE)

        inst_rect = inst.get_rect(center=(self.w // 2, self.frame_rect.bottom + 40))
        # Add background for readability
        bg_rect = inst_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, self.BLACK, bg_rect)
        pygame.draw.rect(self.screen, self.GOLD, bg_rect, 2)
        self.screen.blit(inst, inst_rect)

    def draw_completed_screen(self):
        """Draw the completion screen"""
        # Draw playing screen first
        self.draw_playing_screen()

        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Draw congratulations
        congrats = self.large_font.render("PUZZLE COMPLETE!", True, self.GOLD)
        congrats_rect = congrats.get_rect(center=(self.w // 2, self.h // 2 - 50))
        self.screen.blit(congrats, congrats_rect)

        # Draw completed duck
        if self.duck_image:
            duck_img = pygame.transform.scale(self.duck_image, (300, 200))
            duck_rect = duck_img.get_rect(center=(self.w // 2, self.h // 2 + 30))
            self.screen.blit(duck_img, duck_rect)
            pygame.draw.rect(self.screen, self.GOLD, duck_rect, 3)

        # Draw play again button
        play_again_rect = pygame.Rect(self.w // 2 - 100, self.h // 2 + 150, 200, 60)
        pygame.draw.rect(self.screen, self.GREEN, play_again_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.GOLD, play_again_rect, 3, border_radius=10)

        play_again_text = self.medium_font.render("PLAY AGAIN", True, self.WHITE)
        play_again_text_rect = play_again_text.get_rect(center=play_again_rect.center)
        self.screen.blit(play_again_text, play_again_text_rect)

    def draw_message(self):
        """Draw popup message"""
        if self.message_timer > 0 and self.message:
            msg_surf = self.medium_font.render(self.message, True, self.WHITE)
            msg_rect = msg_surf.get_rect(center=(self.w // 2, 100))

            bubble_rect = msg_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, self.BLACK, bubble_rect, border_radius=15)
            pygame.draw.rect(self.screen, self.GOLD, bubble_rect, 3, border_radius=15)

            self.screen.blit(msg_surf, msg_rect)

    def draw(self):
        # Draw background
        if self.use_bg:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(self.bg_color)

        # Draw based on game state
        if self.game_state == "preview":
            self.draw_preview_screen()
        elif self.game_state == "playing":
            self.draw_playing_screen()
        elif self.game_state == "completed":
            self.draw_completed_screen()

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
            exit_text = self.small_font.render("EXIT", True, self.WHITE)
            exit_text_rect = exit_text.get_rect(center=self.exit_rect.center)
            self.screen.blit(exit_text, exit_text_rect)

        # Draw message
        self.draw_message()

        pygame.display.flip()
        self.clock.tick(self.FPS)
        return self.running