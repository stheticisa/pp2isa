import pygame, random, sys

pygame.init()

# Screen setup
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake with Levels")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED   = (200, 0, 0)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Snake setup
snake = [(100, 100), (80, 100), (60, 100)]
direction = (CELL_SIZE, 0)

# Food setup
def random_food():
    while True:
        pos = (random.randrange(0, WIDTH, CELL_SIZE),
               random.randrange(0, HEIGHT, CELL_SIZE))
        if pos not in snake:
            return pos

food = random_food()

score = 0
level = 1
speed = 10

running = True
while running:
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                direction = (0, -CELL_SIZE)
            elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                direction = (0, CELL_SIZE)
            elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                direction = (-CELL_SIZE, 0)
            elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                direction = (CELL_SIZE, 0)

    # Move snake
    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    # Border collision
    if (new_head[0] < 0 or new_head[0] >= WIDTH or
        new_head[1] < 0 or new_head[1] >= HEIGHT):
        print("Game Over!")
        pygame.quit()
        sys.exit()

    # Self collision
    if new_head in snake:
        print("Game Over!")
        pygame.quit()
        sys.exit()

    snake.insert(0, new_head)

    # Food collision
    if new_head == food:
        score += 1
        food = random_food()
        # Level up every 3 points
        if score % 3 == 0:
            level += 1
            speed += 2
    else:
        snake.pop()

    # Draw snake
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (*segment, CELL_SIZE, CELL_SIZE))

    # Draw food
    pygame.draw.rect(screen, RED, (*food, CELL_SIZE, CELL_SIZE))

    # Draw score and level
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))

    pygame.display.update()
    clock.tick(speed)
