import pygame
import random

# Initialize pygame
pygame.init()

# Set up the window
window = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Game")

x = 200
y = 200

width2 = 50
height2 = 50

width = 20
height = 20

vel = 10

a = random.randint(10, 400)
b = random.randint(10, 400)

score = 0

# Font setup
font = pygame.font.Font(None, 36)

run = True

def display_message(message):
    text = font.render(message, True, (255, 255, 255))
    window.blit(text, (150, 250))
    pygame.display.update()
    pygame.time.delay(2000)  # Delay for 2 seconds

while run:
    pygame.time.delay(10)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()

    # Save the current position
    prev_x, prev_y = x, y

    if keys[pygame.K_LEFT] and x > 0:
        x -= vel

    if keys[pygame.K_RIGHT] and x < 500 - width:
        x += vel

    if keys[pygame.K_UP] and y > 0:
        y -= vel

    if keys[pygame.K_DOWN] and y < 500 - height:
        y += vel

    # Check for collision between the two rectangles
    if x < a + width2 and x + width > a and y < b + height2 and y + height > b:
        a = random.randint(50, 250)
        b = random.randint(50, 250)
        score = score + 1
        width = width + 10
        height += 10
        print("Score:", score)

        # Check if the score is 100
        if score >= 100:
            display_message("Well done, fatty!")
            # Reset the game by setting score, width, height, and player position to initial values
            score = 0
            width = 20
            height = 20
            x = 200
            y = 200
            print("Game Restarted")

    window.fill((100, 30, 45))

    pygame.draw.rect(window, (255, 0, 0), (x, y, width, height))
    pygame.draw.rect(window, (255, 100, 0), (a, b, width2, height2))

    # Render and display the score
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    window.blit(score_text, (10, 10))
    pygame.display.update()

pygame.quit()