import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Player properties
player_size = 50
player_speed = 5

# Enemy properties
enemy_size = 30
enemy_speed = 3

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Platformer")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Player
player = pygame.Rect(WIDTH // 2 - player_size // 2, HEIGHT // 2 - player_size // 2, player_size, player_size)
player_velocity = 0

# Enemies
enemies = [pygame.Rect(random.randint(0, WIDTH-enemy_size), random.randint(0, HEIGHT-enemy_size), enemy_size, enemy_size) for _ in range(5)]

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    player_velocity = 0

    if keys[pygame.K_LEFT]:
        player_velocity = -player_speed
    if keys[pygame.K_RIGHT]:
        player_velocity = player_speed

    player.x += player_velocity

    # Update camera to follow the player
    camera_x = player.x - WIDTH // 2

    # Move enemies
    for enemy in enemies:
        enemy.x -= enemy_speed

        # Check for collisions with player
        if player.colliderect(enemy):
            print("Game Over!")
            pygame.quit()
            sys.exit()

        # Respawn enemies when they go off-screen
        if enemy.right < 0:
            enemy.x = WIDTH
            enemy.y = random.randint(0, HEIGHT-enemy_size)

    # Fill the screen with white
    screen.fill(WHITE)

    # Draw player and enemies relative to the camera position
    pygame.draw.rect(screen, RED, player.move(-camera_x, 0))
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy.move(-camera_x, 0))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate