import pygame, sys, random
from game import Snake, Food, PoisonFood, PowerUp, generate_obstacles
from db import save_result, get_leaderboard, get_personal_best
from config import load_settings

pygame.init()
screen = pygame.display.set_mode((600,600))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial",24)

settings = load_settings()

def main_menu():
    username = ""
    while True:
        screen.fill((0,0,0))
        text = font.render("Enter Username: "+username, True, (255,255,255))
        screen.blit(text,(50,250))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return username
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode

def game_loop(username):
    snake = Snake((10,10))
    food = Food((15,15))
    poison = PoisonFood((20,20))
    score, level = 0, 1
    personal_best = get_personal_best(username)
    obstacles = []

    running = True
    while running:
        screen.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: snake.direction=(0,-1)
                if event.key == pygame.K_DOWN: snake.direction=(0,1)
                if event.key == pygame.K_LEFT: snake.direction=(-1,0)
                if event.key == pygame.K_RIGHT: snake.direction=(1,0)

        snake.move()

        # Collision checks
        if snake.body[0]==food.pos:
            score += food.points
            snake.body.append(snake.body[-1])
            food = Food((random.randint(0,29),random.randint(0,29)))
            if score%5==0:
                level+=1
                obstacles = generate_obstacles(level,snake.body)

        if snake.body[0]==poison.pos:
            if len(snake.body)>2:
                snake.body = snake.body[:-2]
            else:
                running=False

        if snake.body[0] in obstacles:
            running=False

        # Draw
        for seg in snake.body:
            pygame.draw.rect(screen, settings["snake_color"], (seg[0]*20,seg[1]*20,20,20))
        pygame.draw.rect(screen, food.color, (food.pos[0]*20,food.pos[1]*20,20,20))
        pygame.draw.rect(screen, poison.color, (poison.pos[0]*20,poison.pos[1]*20,20,20))
        for obs in obstacles:
            pygame.draw.rect(screen, (100,100,100), (obs[0]*20,obs[1]*20,20,20))

        score_text = font.render(f"Score:{score} Level:{level} PB:{personal_best}", True, (255,255,255))
        screen.blit(score_text,(10,10))

        pygame.display.flip()
        clock.tick(10+level)

    save_result(username, score, level)

def leaderboard_screen():
    rows = get_leaderboard()
    screen.fill((0,0,0))
    y=50
    for i,(u,s,l,d) in enumerate(rows):
        text = font.render(f"{i+1}. {u} {s} {l} {d}", True, (255,255,255))
        screen.blit(text,(50,y))
        y+=30
    pygame.display.flip()
    pygame.time.wait(5000)

if __name__=="__main__":
    user = main_menu()
    game_loop(user)
    leaderboard_screen()
