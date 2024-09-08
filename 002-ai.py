import cv2
import numpy as np
import random

# Initialize game window
width, height = 800, 600
window_name = "Space Invaders"
cv2.namedWindow(window_name)

# Player settings
player_width, player_height = 60, 50
player_x = width // 2 - player_width // 2
player_y = height - 70
player_speed = 20

# Enemy settings
enemy_width, enemy_height = 60, 50
enemy_speed = 5
enemies = []

# Bullet settings
bullet_size = 5
bullet_speed = 10
bullets = []

# Score and game status
score = 0
game_over = False

# Colors
background_color = (0, 0, 0)
player_color = (0, 255, 0)
enemy_color = (0, 0, 255)
bullet_color = (255, 255, 255)
text_color = (255, 255, 255)

# Function to draw the player
def draw_player(img, x, y):
    points = np.array([[x + player_width // 2, y],
                       [x + player_width, y + player_height],
                       [x + player_width * 3 // 4, y + player_height],
                       [x + player_width // 2, y + player_height // 2],
                       [x + player_width // 4, y + player_height],
                       [x, y + player_height]], np.int32)
    points = points.reshape((-1, 1, 2))
    cv2.polylines(img, [points], True, player_color, 3)
    cv2.fillPoly(img, [points], player_color)

# Function to draw enemies
def draw_enemy(img, x, y):
    points = np.array([[x + enemy_width // 2, y],
                       [x + enemy_width, y + enemy_height // 2],
                       [x + enemy_width * 3 // 4, y + enemy_height],
                       [x + enemy_width // 4, y + enemy_height],
                       [x, y + enemy_height // 2]], np.int32)
    points = points.reshape((-1, 1, 2))
    cv2.polylines(img, [points], True, enemy_color, 3)
    cv2.fillPoly(img, [points], enemy_color)

# Function to draw bullets
def draw_bullets(img, bullets):
    for bullet in bullets:
        cv2.circle(img, (bullet[0], bullet[1]), bullet_size, bullet_color, -1)

# Function to detect collisions
def check_collision(enemy, bullet):
    return bullet[0] > enemy[0] and bullet[0] < enemy[0] + enemy_width and bullet[1] > enemy[1] and bullet[1] < enemy[1] + enemy_height

# Function to find the closest enemy
def find_closest_enemy(enemies, player_x):
    closest_enemy = None
    min_distance = float('inf')
    for enemy in enemies:
        distance = abs(player_x + player_width // 2 - (enemy[0] + enemy_width // 2))
        if distance < min_distance:
            min_distance = distance
            closest_enemy = enemy
    return closest_enemy

# Game loop
while not game_over:
    # Create a black background
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Draw player
    draw_player(frame, player_x, player_y)

    # Draw enemies
    for enemy in enemies:
        draw_enemy(frame, enemy[0], enemy[1])

    # Draw bullets
    draw_bullets(frame, bullets)

    # Move enemies
    for enemy in enemies:
        enemy[1] += enemy_speed
        if enemy[1] > height:
            game_over = True

    # Move bullets
    new_bullets = []
    for bullet in bullets:
        bullet[1] -= bullet_speed
        if bullet[1] > 0:
            new_bullets.append(bullet)
    bullets = new_bullets

    # Check for collisions
    new_enemies = []
    for enemy in enemies:
        hit = False
        for bullet in bullets:
            if check_collision(enemy, bullet):
                bullets.remove(bullet)
                score += 1
                hit = True
                break
        if not hit:
            new_enemies.append(enemy)
    enemies = new_enemies

    # AI logic
    closest_enemy = find_closest_enemy(enemies, player_x)
    if closest_enemy:
        # Move player towards the closest enemy
        if closest_enemy[0] + enemy_width // 2 < player_x + player_width // 2:
            player_x -= player_speed
        elif closest_enemy[0] + enemy_width // 2 > player_x + player_width // 2:
            player_x += player_speed

        # Shoot if aligned with the closest enemy
        if abs(closest_enemy[0] + enemy_width // 2 - (player_x + player_width // 2)) < player_speed:
            bullets.append([player_x + player_width // 2, player_y])

    # Display score
    cv2.putText(frame, f'Score: {score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2, cv2.LINE_AA)

    # Show frame
    cv2.imshow(window_name, frame)

    # Handle key press to exit
    key = cv2.waitKey(30)
    if key == 27:  # ESC to quit
        break

    # Spawn new enemy
    if random.randint(1, 20) == 1:
        enemies.append([random.randint(0, width - enemy_width), 0])

cv2.destroyAllWindows()
