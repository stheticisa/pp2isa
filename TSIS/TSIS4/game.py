import pygame, random
from db import save_result, get_personal_best
from config import load_settings

# Snake, Food, Poison, PowerUp, Obstacles classes

class Snake:
    def __init__(self, pos):
        self.body = [pos]
        self.direction = (1,0)

    def move(self):
        head = (self.body[0][0]+self.direction[0], self.body[0][1]+self.direction[1])
        self.body.insert(0, head)
        self.body.pop()

class Food:
    def __init__(self, pos, points=1):
        self.pos = pos
        self.points = points
        self.color = (255,0,0)

class PoisonFood:
    def __init__(self, pos):
        self.pos = pos
        self.color = (139,0,0)

class PowerUp:
    def __init__(self, pos, type):
        self.pos = pos
        self.type = type
        self.spawn_time = pygame.time.get_ticks()
        self.color = {"speed":(0,255,0),"slow":(0,0,255),"shield":(255,255,0)}[type]

def generate_obstacles(level, snake_pos):
    obstacles = []
    if level >= 3:
        for _ in range(level):
            pos = (random.randint(0,29), random.randint(0,29))
            while pos in snake_pos or pos in obstacles:
                pos = (random.randint(0,29), random.randint(0,29))
            obstacles.append(pos)
    return obstacles
