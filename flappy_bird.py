import pygame
import random
import sys
import torch
from genetic import network, mutate_model
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 250)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Game variables
gravity = 0.5
bird_jump = -10
bird_x = 50
bird_y = HEIGHT // 2
bird_radius = 15
bird_velocity = 0

pipe_width = 70
pipe_gap = 150
pipe_speed = 5
pipe_frequency = 1500  # milliseconds

run = 0
high_score = 0
best_run = 0

# Font
font = pygame.font.Font(None, 36)

# Clock
clock = pygame.time.Clock()

# Generate pipes
def create_pipe():
    height = random.randint(100, HEIGHT - pipe_gap - 100)
    return [pygame.Rect(WIDTH, 0, pipe_width, height),  # Top pipe
            pygame.Rect(WIDTH, height + pipe_gap, pipe_width, HEIGHT - height - pipe_gap)]  # Bottom pipe

pipes = [create_pipe()]

class Bird:
    def __init__(self, model):
        self.x = bird_x
        self.y = bird_y
        self.velocity = 0
        self.alive = True
        self.score = 0
        self.model = model

birds = [Bird(network(3)) for _ in range(350)]
clock = pygame.time.Clock()

def reset_simulation(obj: Bird):
    global pipes, birds, elapsed_time
    pipes = [create_pipe()]
    elapsed_time = 0
    return [Bird(mutate_model(obj.model)) for _ in range(350)]


# Game loop
running = True
while running:
    delta_time = clock.tick(60) / 1000
    screen.fill(BLUE)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move and draw pipes
    for pipe_pair in pipes:
        for pipe in pipe_pair:
            pipe.x -= pipe_speed
            pygame.draw.rect(screen, GREEN, pipe)

    # Add new pipes
    if pipes[-1][0].x < WIDTH - pipe_frequency // pipe_speed:
        pipes.append(create_pipe())

    # Remove off-screen pipes
    if pipes[0][0].x + pipe_width < 0:
        pipes.pop(0)
        pipe_speed += 0.1

    # all_dead = True
    for bird in birds:

        if not bird.alive:
            continue

        # if bird.alive:
        #     all_dead = False

        bird_list = [np.float32(bird.velocity + pipe_speed), np.float32(bird.x - pipes[0][0].x), np.float32(bird.y - pipes[0][0].height)]
        if bird.model(torch.tensor(bird_list)) == 1:
            bird.velocity = bird_jump
        bird.velocity += gravity
        bird.y += bird.velocity

        if bird.alive:
            pygame.draw.circle(screen, RED, (bird.x, int(bird.y)), bird_radius)

        # Check for collisions
        bird_rect = pygame.Rect(bird.x - bird_radius, bird.y - bird_radius, bird_radius * 2, bird_radius * 2)
        for pipe_pair in pipes:
            if bird_rect.colliderect(pipe_pair[0]) or bird_rect.colliderect(pipe_pair[1]):
                bird.alive = False

        # Check if bird hits the ground or goes off-screen
        if bird.y - bird_radius < 0 or bird.y + bird_radius > HEIGHT:
            bird.alive = False

        bird.score += delta_time
    
    all_dead = sum(1 for obj in birds if obj.alive) == 0
    # alive_objects = [obj for obj in birds if obj.alive]

    if all_dead:
        max_score_object = max(birds, key=lambda obj: obj.score)
        pipe_speed = 5
        if run == 0:
            best_object = max_score_object
        if max_score_object.score > high_score:
            best_run = run
            best_object = max_score_object
        run += 1
        high_score =  max(high_score, max_score_object.score)
        birds = reset_simulation(best_object)
        
    # Display score
    score_text = font.render(f"High Score: {round(high_score, 2)} | Run: {run}", True, WHITE)
    screen.blit(score_text, (10, 10))
    score_text = font.render(f"Best Run:{best_run}", True, WHITE)
    screen.blit(score_text, (10, 40))
    score_text = font.render(f"Speed:{round(pipe_speed, 1)}", True, WHITE)
    screen.blit(score_text, (10, 70))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
