import pygame
import random
import pygame_gui

# Initialize Pygame
pygame.init()

# Set up the game window
screen_width = 800
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Ping Pong")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the game clock
clock = pygame.time.Clock()

# Create the GUI manager
gui_manager = pygame_gui.UIManager((screen_width, screen_height))

# Create the player name input textbox
player_name_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect = pygame.Rect((screen_width // 2 - 100, screen_height // 2 - 60), (200, 40)),
    manager = gui_manager
)

# Create the name inscription label
name_inscription_label = pygame_gui.elements.UILabel(
    relative_rect = pygame.Rect((screen_width // 2 - 100, screen_height // 2 - 110), (200, 40)),
    text = "Enter your name here",
    manager = gui_manager
)

# Create the game mode dropdown menu
game_mode_options = [
    "Play with another player",
    "Play with the computer"
]

game_mode_dropdown = pygame_gui.elements.UIDropDownMenu(
    options_list=game_mode_options,
    starting_option=game_mode_options[0],
    relative_rect=pygame.Rect((screen_width // 2 - 100, screen_height // 2 + 30), (200, 40)),
    manager=gui_manager
)

# Create the start button
start_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((screen_width // 2 - 50, screen_height // 2 + 80), (100, 40)),
    text="Start",
    manager=gui_manager
)

# Define the game elements
ball_radius = 10
paddle_width = 10
paddle_height = 60
ball_speed = 4
paddle_speed = 4

# Create the ball sprite
ball = pygame.Rect(screen_width // 2 - ball_radius, screen_height // 2 - ball_radius, ball_radius * 2, ball_radius * 2)
ball_speed_x = ball_speed
ball_speed_y = ball_speed

# Create the paddles
player_paddle = pygame.Rect(50, screen_height // 2 - paddle_height // 2, paddle_width, paddle_height)
computer_paddle = pygame.Rect(screen_width - 50 - paddle_width, screen_height // 2 - paddle_height // 2, paddle_width, paddle_height)

# Set up the game variables
player_score = 0
computer_score = 0
font = pygame.font.Font(None, 36)

# Power-up variables
player_power_up = False
power_up_duration = 30 * 60  # 30 seconds at 60 FPS
power_up_timer = 0

# Game over messages
win_message = "You win!"
lose_message = "You lose!"
game_over_message = ""

# Function to restart the game
def restart_game():
    global ball_speed_x, ball_speed_y
    ball.center = (screen_width // 2, screen_height // 2)
    ball_speed_x *= random.choice([1, -1])
    ball_speed_y *= random.choice([1, -1])

# Set up the game loop
running = True
game_started = False

# Load and play the song
pygame.mixer.init()
pygame.mixer.music.load("son.mp3")
pygame.mixer.music.play(-1)

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    player_name = player_name_textbox.get_text()
                    game_mode_text = game_mode_dropdown.selected_option

                    game_mode = game_mode_options.index(game_mode_text) + 1
                    game_started = True
        elif event.type == pygame.VIDEORESIZE:
            screen_width = event.w
            screen_height = event.h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

            player_paddle.y = screen_height // 2 - paddle_height // 2
            # Update the position of the computer paddle relative to the new screen dimensions
            computer_paddle.y = screen_height // 2 - computer_paddle.height // 2
            computer_paddle.x = screen_width - 50 - paddle_width

        gui_manager.process_events(event)

    gui_manager.update(time_delta)

    if not game_started:
        screen.fill(WHITE)
        gui_manager.draw_ui(screen)
        pygame.display.update()
        continue

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_paddle.y -= paddle_speed
    if keys[pygame.K_DOWN]:
        player_paddle.y += paddle_speed
    if keys[pygame.K_k] and not player_power_up:
        player_paddle.height *= 2
        paddle_speed /= 2
        player_power_up = True
        power_up_timer = power_up_duration

    # Update ball position
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Ball collisions with paddles
    if ball.colliderect(player_paddle) or ball.colliderect(computer_paddle):
        ball_speed_x *= -1

    # Ball collisions with walls
    if ball.top <= 0 or ball.bottom >= screen_height:
        ball_speed_y *= -1

    # Check if the player missed the ball
    if ball.left <= 0:
        computer_score += 1
        restart_game()

    # Check if the computer missed the ball
    if ball.right >= screen_width:
        player_score += 1
        restart_game()

    # AI logic for computer paddle
    if game_mode == 2 and ball_speed_x > 0:
        if ball.centery < computer_paddle.centery:
            computer_paddle.y -= paddle_speed
        elif ball.centery > computer_paddle.centery:
            computer_paddle.y += paddle_speed

    # Change color based on screen side
    if ball.x < screen_width // 2:
        background_color = BLACK
        paddle_color = WHITE
        ball_color = WHITE
    else:
        background_color = WHITE
        paddle_color = BLACK
        ball_color = BLACK

    # Update the game elements
    player_score_text = font.render(player_name + ": " + str(player_score), True, paddle_color)
    computer_score_text = font.render("Computer: " + str(computer_score), True, paddle_color)

    # Draw the game elements
    screen.fill(background_color)
    pygame.draw.rect(screen, paddle_color, player_paddle)
    pygame.draw.rect(screen, paddle_color, computer_paddle)
    pygame.draw.ellipse(screen, ball_color, ball)
    pygame.draw.aaline(screen, paddle_color, (screen_width // 2, 0), (screen_width // 2, screen_height))
    screen.blit(player_score_text, (20, 20))
    screen.blit(computer_score_text, (screen_width - computer_score_text.get_width() - 20, 20))

    # Update the power-up timer
    if player_power_up:
        power_up_timer -= 1
        if power_up_timer <= 0:
            player_paddle.height //= 2
            paddle_speed *= 2
            player_power_up = False

    # Check if any player has won the game
    if player_score >= 7:
        game_over_message = "You win!"
        running = False
    elif computer_score >= 7:
        if game_mode == 1:
            game_over_message = "Player 2 wins!"
        else:
            game_over_message = "Computer wins!"
        running = False

    pygame.display.update()

# Display game over message
game_over_text = font.render(game_over_message, True, paddle_color)
screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - game_over_text.get_height() // 2))
pygame.display.update()

# Wait for a few seconds before quitting
pygame.time.wait(3000)

# Stop the song
pygame.mixer.music.stop()

# Quit Pygame
pygame.quit()
