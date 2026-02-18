# C:\Users\Levnicolayevich\PycharmProjects\PythonProject\screens\mazegame.py
import pygame
import os
import sys
import random


class MazeGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        # Load background
        bg_path = os.path.join("assets", "images", "menu_background.png")
        self.bg_image = pygame.image.load(bg_path).convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (self.width, self.height))

        # Colors
        self.BACKGROUND = (240, 245, 255, 200)
        self.WALL_COLOR = (100, 100, 150)
        self.PATH_COLOR = (255, 255, 255, 200)
        self.PLAYER_COLOR = (255, 100, 100)
        self.EXIT_COLOR = (100, 255, 100)
        self.TEXT_COLOR = (50, 50, 50)
        self.LETTER_COLORS = [
            (255, 50, 50),  # A - Red
            (50, 150, 255),  # B - Blue
            (255, 200, 50),  # C - Yellow
            (150, 50, 255)  # D - Purple
        ]

        # Game configuration
        self.grid_size = 15  # Bigger 15x15 maze
        self.cell_size = min(self.width, self.height) // (self.grid_size + 3)

        # Initialize game state
        self.reset_game()

        # Font
        self.title_font = pygame.font.SysFont("Comic Sans MS", 48, bold=True)
        self.font = pygame.font.SysFont("Comic Sans MS", 32, bold=True)
        self.small_font = pygame.font.SysFont("Comic Sans MS", 24, bold=True)
        self.letter_font = pygame.font.SysFont("Comic Sans MS", 28, bold=True)

        # Back button
        back_image_path = os.path.join("assets", "images", "exitbutton.png")
        self.back_image = pygame.image.load(back_image_path).convert_alpha()
        self.back_button = pygame.Rect(20, 20, 120, 60)
        self.back_image = pygame.transform.scale(self.back_image, (self.back_button.width, self.back_button.height))

        # Generate initial maze
        self.generate_maze()
        self.place_letters()
        self.place_exit()

    def generate_maze(self):
        """Generate a random maze with a single path solution"""
        # Initialize with all walls
        self.maze = [[1 for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Start position (always at top-left)
        self.start_pos = [1, 1]
        self.player_pos = self.start_pos.copy()

        # Create paths using recursive backtracking
        stack = [self.start_pos]
        visited = set()
        visited.add(tuple(self.start_pos))

        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]

        while stack:
            current = stack[-1]
            x, y = current

            # Get unvisited neighbors
            neighbors = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (1 <= nx < self.grid_size - 1 and 1 <= ny < self.grid_size - 1 and
                        (nx, ny) not in visited):
                    neighbors.append((nx, ny, dx // 2, dy // 2))

            if neighbors:
                # Choose random neighbor
                nx, ny, dx, dy = random.choice(neighbors)

                # Carve path
                self.maze[y][x] = 0  # Current cell
                self.maze[ny][nx] = 0  # Next cell
                self.maze[y + dy][x + dx] = 0  # Cell between them

                visited.add((nx, ny))
                stack.append([nx, ny])
            else:
                stack.pop()

        # Ensure start and player positions are clear
        self.maze[self.start_pos[1]][self.start_pos[0]] = 0

        # Add some random extra paths for complexity
        for _ in range(self.grid_size * 2):
            x = random.randint(1, self.grid_size - 2)
            y = random.randint(1, self.grid_size - 2)
            if self.maze[y][x] == 1:
                # Check if removing this wall creates a valid path
                path_count = 0
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        if self.maze[ny][nx] == 0:
                            path_count += 1
                if path_count >= 2:
                    self.maze[y][x] = 0

    def place_letters(self):
        """Place letters A-D in the maze at random accessible locations"""
        self.letters = []
        self.collected_letters = []
        self.current_target_letter = 0  # 0=A, 1=B, 2=C, 3=D

        # Find all accessible path positions (excluding start)
        accessible_positions = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.maze[y][x] == 0 and [x, y] != self.start_pos:
                    accessible_positions.append([x, y])

        if len(accessible_positions) >= 4:
            # Randomly select 4 positions for letters
            letter_positions = random.sample(accessible_positions, 4)

            for i, (x, y) in enumerate(letter_positions):
                self.letters.append({
                    'pos': [x, y],
                    'letter': chr(65 + i),  # A, B, C, D
                    'collected': False,
                    'index': i
                })
        else:
            # Fallback positions if not enough space
            fallback_positions = [
                [self.grid_size // 2, 1],
                [self.grid_size - 2, self.grid_size // 2],
                [self.grid_size // 2, self.grid_size - 2],
                [1, self.grid_size // 2]
            ]
            for i, (x, y) in enumerate(fallback_positions):
                self.maze[y][x] = 0  # Ensure it's a path
                self.letters.append({
                    'pos': [x, y],
                    'letter': chr(65 + i),
                    'collected': False,
                    'index': i
                })

    def place_exit(self):
        """Place exit at a random location far from start"""
        # Find positions that are far from start
        exit_candidates = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.maze[y][x] == 0:
                    # Calculate distance from start
                    distance = abs(x - self.start_pos[0]) + abs(y - self.start_pos[1])
                    # Ensure exit is not on a letter position
                    on_letter = any(letter['pos'] == [x, y] for letter in self.letters)
                    if distance > self.grid_size // 2 and not on_letter:
                        exit_candidates.append([x, y])

        if exit_candidates:
            self.exit_pos = random.choice(exit_candidates)
        else:
            # Fallback: bottom-right corner
            self.exit_pos = [self.grid_size - 2, self.grid_size - 2]
            self.maze[self.exit_pos[1]][self.exit_pos[0]] = 0

    def reset_game(self):
        """Reset the game to initial state"""
        self.game_over = False
        self.victory = False
        self.collected_letters = []
        self.current_target_letter = 0
        self.start_time = pygame.time.get_ticks()

    def find_letter_at_position(self, x, y):
        """Find if there's a letter at the given position"""
        for letter in self.letters:
            if letter['pos'] == [x, y] and not letter['collected']:
                return letter
        return None

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if not self.game_over:
                self.handle_movement(event.key)

            # Restart game with R key
            if event.key == pygame.K_r:
                self.generate_maze()
                self.place_letters()
                self.place_exit()
                self.reset_game()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.back_button.collidepoint(event.pos):
                    return "back"
        return None

    def handle_movement(self, key):
        """Handle WASD and arrow key movement"""
        new_x, new_y = self.player_pos[0], self.player_pos[1]

        # WASD keys
        if key == pygame.K_w:
            new_y -= 1
        elif key == pygame.K_s:
            new_y += 1
        elif key == pygame.K_a:
            new_x -= 1
        elif key == pygame.K_d:
            new_x += 1
        # Arrow keys (optional)
        elif key == pygame.K_UP:
            new_y -= 1
        elif key == pygame.K_DOWN:
            new_y += 1
        elif key == pygame.K_LEFT:
            new_x -= 1
        elif key == pygame.K_RIGHT:
            new_x += 1
        else:
            return

        # Check boundaries
        if (0 <= new_x < self.grid_size) and (0 <= new_y < self.grid_size):
            # Check if new position is walkable (not a wall)
            if self.maze[new_y][new_x] != 1:
                self.player_pos = [new_x, new_y]

                # Check for letter collection
                letter = self.find_letter_at_position(new_x, new_y)
                if letter:
                    # Check if this is the next letter in sequence
                    if letter['index'] == self.current_target_letter:
                        letter['collected'] = True
                        self.collected_letters.append(letter['letter'])
                        self.current_target_letter += 1
                        print(f"Collected letter {letter['letter']}!")

                # Check if reached exit (only if all letters collected)
                if (self.player_pos == self.exit_pos and
                        len(self.collected_letters) == 4):
                    self.game_over = True
                    self.victory = True
                    self.completion_time = (pygame.time.get_ticks() - self.start_time) // 1000

    def draw(self):
        """Draw the entire game"""
        # Draw background
        self.screen.blit(self.bg_image, (0, 0))

        # Draw semi-transparent overlay for game area
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((240, 245, 255, 200))
        self.screen.blit(overlay, (0, 0))

        # Draw title
        title = self.title_font.render("Alphabet Maze Adventure", True, (70, 70, 120))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 30))

        # Draw instructions
        instructions = self.small_font.render("Use WASD to move. Collect A→B→C→D then find EXIT", True, (100, 100, 150))
        self.screen.blit(instructions, (self.width // 2 - instructions.get_width() // 2, 90))

        # Calculate maze position to center it
        maze_width = self.grid_size * self.cell_size
        maze_height = self.grid_size * self.cell_size
        maze_x = (self.width - maze_width) // 2
        maze_y = (self.height - maze_height) // 2 + 50

        # Draw maze
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                cell_rect = pygame.Rect(
                    maze_x + x * self.cell_size,  # FIXED: Changed self.maze to self.cell_size
                    maze_y + y * self.cell_size,  # FIXED: Changed self.maze to self.cell_size
                    self.cell_size,
                    self.cell_size
                )

                # Draw cell based on type
                if [x, y] == self.exit_pos:
                    # Draw exit
                    pygame.draw.rect(self.screen, self.EXIT_COLOR, cell_rect, border_radius=8)
                    exit_text = self.font.render("EXIT", True, (0, 100, 0))
                    text_rect = exit_text.get_rect(center=cell_rect.center)
                    self.screen.blit(exit_text, text_rect)
                elif self.maze[y][x] == 1:  # Wall
                    pygame.draw.rect(self.screen, self.WALL_COLOR, cell_rect, border_radius=5)
                    pygame.draw.rect(self.screen, (80, 80, 120), cell_rect, 2, border_radius=5)
                elif [x, y] == self.start_pos:  # Start
                    pygame.draw.rect(self.screen, (200, 200, 255), cell_rect, border_radius=8)
                    start_text = self.small_font.render("START", True, (50, 50, 150))
                    text_rect = start_text.get_rect(center=cell_rect.center)
                    self.screen.blit(start_text, text_rect)
                else:  # Path
                    pygame.draw.rect(self.screen, self.PATH_COLOR, cell_rect, border_radius=5)
                    pygame.draw.rect(self.screen, (200, 200, 220), cell_rect, 1, border_radius=5)

        # Draw letters
        for letter_data in self.letters:
            x, y = letter_data['pos']
            cell_rect = pygame.Rect(
                maze_x + x * self.cell_size,
                maze_y + y * self.cell_size,
                self.cell_size,
                self.cell_size
            )

            if not letter_data['collected']:
                # Only show letter if it's the current target or already collected previous ones
                if letter_data['index'] <= self.current_target_letter:
                    # Draw letter with glow effect for current target
                    if letter_data['index'] == self.current_target_letter:
                        # Glow effect
                        glow_rect = cell_rect.inflate(10, 10)
                        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                        pygame.draw.rect(glow_surf, (*self.LETTER_COLORS[letter_data['index']], 100),
                                         glow_surf.get_rect(), border_radius=10)
                        self.screen.blit(glow_surf, glow_rect)

                    # Draw letter circle
                    pygame.draw.rect(self.screen, self.LETTER_COLORS[letter_data['index']],
                                     cell_rect.inflate(-10, -10), border_radius=15)

                    # Draw letter
                    letter_text = self.letter_font.render(letter_data['letter'], True, (255, 255, 255))
                    text_rect = letter_text.get_rect(center=cell_rect.center)
                    self.screen.blit(letter_text, text_rect)
                else:
                    # Show locked letter (grayed out)
                    pygame.draw.rect(self.screen, (150, 150, 150),
                                     cell_rect.inflate(-10, -10), border_radius=15)
                    lock_text = self.small_font.render("?", True, (200, 200, 200))
                    text_rect = lock_text.get_rect(center=cell_rect.center)
                    self.screen.blit(lock_text, text_rect)

        # Draw player
        player_rect = pygame.Rect(
            maze_x + self.player_pos[0] * self.cell_size + self.cell_size // 4,
            maze_y + self.player_pos[1] * self.cell_size + self.cell_size // 4,
            self.cell_size // 2,
            self.cell_size // 2
        )
        pygame.draw.rect(self.screen, self.PLAYER_COLOR, player_rect, border_radius=10)

        # Draw eyes on player
        eye_size = self.cell_size // 10
        pygame.draw.circle(self.screen, (255, 255, 255),
                           (player_rect.left + player_rect.width // 3,
                            player_rect.top + player_rect.height // 3),
                           eye_size)
        pygame.draw.circle(self.screen, (255, 255, 255),
                           (player_rect.right - player_rect.width // 3,
                            player_rect.top + player_rect.height // 3),
                           eye_size)
        pygame.draw.circle(self.screen, (0, 0, 0),
                           (player_rect.left + player_rect.width // 3,
                            player_rect.top + player_rect.height // 3),
                           eye_size // 2)
        pygame.draw.circle(self.screen, (0, 0, 0),
                           (player_rect.right - player_rect.width // 3,
                            player_rect.top + player_rect.height // 3),
                           eye_size // 2)

        # Draw progress panel on the right
        panel_width = 200
        panel_rect = pygame.Rect(self.width - panel_width - 20, 150, panel_width, 300)
        pygame.draw.rect(self.screen, (255, 255, 255, 220), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (180, 180, 220), panel_rect, 3, border_radius=15)

        # Draw panel title
        progress_title = self.font.render("Progress", True, (70, 70, 120))
        self.screen.blit(progress_title, (panel_rect.centerx - progress_title.get_width() // 2, panel_rect.top + 20))

        # Draw collected letters
        y_offset = 70
        for i, letter in enumerate(['A', 'B', 'C', 'D']):
            letter_rect = pygame.Rect(panel_rect.left + 40, panel_rect.top + y_offset, 40, 40)

            if i < len(self.collected_letters):
                # Collected letter
                pygame.draw.rect(self.screen, self.LETTER_COLORS[i], letter_rect, border_radius=10)
                letter_text = self.letter_font.render(letter, True, (255, 255, 255))
                check_text = self.small_font.render("✓", True, (0, 200, 0))
            elif i == self.current_target_letter:
                # Current target
                pygame.draw.rect(self.screen, self.LETTER_COLORS[i], letter_rect, border_radius=10)
                letter_text = self.letter_font.render(letter, True, (255, 255, 255))
                check_text = self.small_font.render("→", True, (255, 255, 0))
            else:
                # Not yet available
                pygame.draw.rect(self.screen, (200, 200, 200), letter_rect, border_radius=10)
                letter_text = self.letter_font.render(letter, True, (150, 150, 150))
                check_text = self.small_font.render("", True, (0, 0, 0))

            text_rect = letter_text.get_rect(center=letter_rect.center)
            self.screen.blit(letter_text, text_rect)

            # Draw checkmark or arrow
            check_rect = check_text.get_rect(left=letter_rect.right + 10, centery=letter_rect.centery)
            self.screen.blit(check_text, check_rect)

            y_offset += 60

        # Draw back button
        self.screen.blit(self.back_image, self.back_button)

        # Draw game over/victory message
        if self.game_over and self.victory:
            # Semi-transparent overlay
            victory_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            victory_overlay.fill((0, 0, 0, 180))
            self.screen.blit(victory_overlay, (0, 0))

            # Victory message
            victory_text = self.title_font.render("You Won!", True, (255, 215, 0))
            time_text = self.font.render(f"Time: {self.completion_time} seconds", True, (255, 255, 255))
            letters_text = self.font.render("Collected: A B C D", True, (200, 255, 200))
            restart_text = self.small_font.render("Press 'R' to play again or click Back", True, (200, 200, 255))

            self.screen.blit(victory_text, (self.width // 2 - victory_text.get_width() // 2,
                                            self.height // 2 - 120))
            self.screen.blit(time_text, (self.width // 2 - time_text.get_width() // 2,
                                         self.height // 2 - 60))
            self.screen.blit(letters_text, (self.width // 2 - letters_text.get_width() // 2,
                                            self.height // 2 - 20))
            self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2,
                                            self.height // 2 + 30))

            # Draw trophy and letters display
            trophy_y = self.height // 2 - 220
            for i, letter in enumerate(['A', 'B', 'C', 'D']):
                letter_x = self.width // 2 - 120 + i * 60
                letter_rect = pygame.Rect(letter_x, trophy_y, 50, 50)
                pygame.draw.rect(self.screen, self.LETTER_COLORS[i], letter_rect, border_radius=10)
                letter_text = self.font.render(letter, True, (255, 255, 255))
                text_rect = letter_text.get_rect(center=letter_rect.center)
                self.screen.blit(letter_text, text_rect)

                # Draw checkmark above each collected letter
                check_text = self.font.render("✓", True, (0, 255, 0))
                self.screen.blit(check_text, (letter_rect.centerx - 10, letter_rect.top - 30))

    def update(self):
        """Update game logic"""
        pass