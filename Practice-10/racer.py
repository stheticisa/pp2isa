import pygame, random, sys

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer with Coins")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (200, 0, 0)
YELLOW = (255, 215, 0)

# Clock for FPS
clock = pygame.time.Clock()

# Player car
player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 80, 50, 80)

# Enemy car
enemy = pygame.Rect(random.randint(50, WIDTH-100), -100, 50, 80)

# Coin setup
coin = pygame.Rect(random.randint(50, WIDTH-50), -50, 30, 30)
coins_collected = 0

# Fonts
font = pygame.font.SysFont("Arial", 24)

def reset_enemy():
    enemy.x = random.randint(50, WIDTH-100)
    enemy.y = -100

def reset_coin():
    coin.x = random.randint(50, WIDTH-50)
    coin.y = -50

# Game loop
running = True
while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.move_ip(-5, 0)
    if keys[pygame.K_RIGHT] and player.right < WIDTH:
        player.move_ip(5, 0)

    # Enemy movement
    enemy.move_ip(0, 5)
    if enemy.top > HEIGHT:
        reset_enemy()

    # Coin movement
    coin.move_ip(0, 4)
    if coin.top > HEIGHT:
        reset_coin()

    # Collision detection
    if player.colliderect(enemy):
        print("Game Over!")
        pygame.quit()
        sys.exit()

    if player.colliderect(coin):
        coins_collected += 1
        reset_coin()

    # Draw objects
    pygame.draw.rect(screen, RED, player)
    pygame.draw.rect(screen, BLACK, enemy)
    pygame.draw.circle(screen, YELLOW, coin.center, 15)

    # Draw coin counter
    score_text = font.render(f"Coins: {coins_collected}", True, BLACK)
    screen.blit(score_text, (WIDTH - 120, 20))

    pygame.display.update()
    clock.tick(60)
