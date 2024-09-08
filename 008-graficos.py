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
targeted_enemies = []  # List for enemies currently being targeted

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

# Updated function to draw '80s style enemy ships
def draw_enemy(img, x, y):
    # Body of the spaceship (a central rectangle)
    body_width = int(enemy_width * 0.8)
    body_height = int(enemy_height * 0.6)
    body_x = x + (enemy_width - body_width) // 2
    body_y = y + (enemy_height - body_height) // 2
    cv2.rectangle(img, (body_x, body_y), (body_x + body_width, body_y + body_height), enemy_color, -1)

    # Top antenna (a small rectangle on top of the body)
    antenna_width = int(body_width * 0.2)
    antenna_height = int(body_height * 0.3)
    antenna_x = body_x + (body_width - antenna_width) // 2
    antenna_y = body_y - antenna_height
    cv2.rectangle(img, (antenna_x, antenna_y), (antenna_x + antenna_width, antenna_y + antenna_height), enemy_color, -1)

    # Wings (two triangles on the sides)
    wing_height = int(body_height * 0.5)
    left_wing_points = np.array([[x, y + body_height // 2],
                                 [body_x, y + body_height // 2 - wing_height],
                                 [body_x, y + body_height // 2 + wing_height]], np.int32)
    right_wing_points = np.array([[x + enemy_width, y + body_height // 2],
                                  [body_x + body_width, y + body_height // 2 - wing_height],
                                  [body_x + body_width, y + body_height // 2 + wing_height]], np.int32)
    cv2.fillPoly(img, [left_wing_points], enemy_color)
    cv2.fillPoly(img, [right_wing_points], enemy_color)

    # Cockpit (a small circle on the body)
    cockpit_radius = int(body_width * 0.1)
    cockpit_center = (body_x + body_width // 2, body_y + body_height // 2)
    cv2.circle(img, cockpit_center, cockpit_radius, bullet_color, -1)

# Function to draw bullets
def draw_bullets(img, bullets):
    for bullet in bullets:
        cv2.circle(img, (bullet[0], bullet[1]), bullet_size, bullet_color, -1)

# Function to detect collisions
def check_collision(enemy, bullet):
    return bullet[0] > enemy[0] and bullet[0] < enemy[0] + enemy_width and bullet[1] > enemy[1] and bullet[1] < enemy[1] + enemy_height

# Function to find the closest enemy not already targeted by a bullet
def find_closest_enemy(enemies, player_x, targeted_enemies):
    closest_enemy = None
    min_distance = float('inf')

    for enemy in enemies:
        if enemy in targeted_enemies:
            continue  # Skip enemies already targeted by a bullet
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
    for enemy in enemies + targeted_enemies:
        draw_enemy(frame, enemy[0], enemy[1])

    # Draw bullets
    draw_bullets(frame, bullets)

    # Move enemies
    for enemy in enemies + targeted_enemies:
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
    new_targeted_enemies = []
    for enemy in targeted_enemies:
        hit = False
        for bullet in bullets:
            if check_collision(enemy, bullet):
                bullets.remove(bullet)
                score += 1
                hit = True
                break
        if not hit:
            new_targeted_enemies.append(enemy)
    targeted_enemies = new_targeted_enemies

    for enemy in enemies:
        if enemy not in targeted_enemies:
            new_enemies.append(enemy)
    enemies = new_enemies

    # AI logic
    closest_enemy = find_closest_enemy(enemies, player_x, targeted_enemies)
    if closest_enemy:
        # Move player towards the closest enemy
        if closest_enemy[0] + enemy_width // 2 < player_x + player_width // 2:
            player_x -= player_speed
        elif closest_enemy[0] + enemy_width // 2 > player_x + player_width // 2:
            player_x += player_speed

        # Shoot if aligned with the closest enemy
        if abs(closest_enemy[0] + enemy_width // 2 - (player_x + player_width // 2)) < player_speed:
            bullets.append([player_x + player_width // 2, player_y])
            targeted_enemies.append(closest_enemy)  # Add the targeted enemy to the list of targeted enemies

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
