import pygame
import os
import sys
import random

pygame.mixer.init()
pygame.init()

game_font = pygame.font.Font("04B_19.ttf",40)

# Game settings
WIDTH = 600
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
FPS = 60
pygame.display.set_caption("Python - Flappy Bird")

# Load images
BG = pygame.image.load(os.path.join("assets", "background_clouds_flappybird_original.png")).convert()
BG = pygame.transform.scale(BG,(WIDTH, HEIGHT))

FLOOR_HEIGHT = 95
FLOOR = pygame.image.load(os.path.join("assets", "base_5x.png")).convert()

bird_downflap = pygame.image.load(os.path.join("assets", "bird-downflap.png")).convert_alpha()
bird_midflap = pygame.image.load(os.path.join("assets", "bird-midflap.png")).convert_alpha()
bird_upflap = pygame.image.load(os.path.join("assets", "bird-upflap.png")).convert_alpha()
bird_frames = [bird_downflap,bird_midflap,bird_upflap]
bird_index = 0
BIRD = bird_frames[bird_index]
BIRD_RECT = BIRD.get_rect(center = (300, 480))

FLAP_SOUND = pygame.mixer.Sound("sound/sfx_wing.wav")
DEATH_SOUND = pygame.mixer.Sound("sound/sfx_hit.wav")
SCORE_SOUND = pygame.mixer.Sound("sound/sfx_point.wav")

pygame.mixer.Sound.set_volume(FLAP_SOUND, 0.25)
pygame.mixer.Sound.set_volume(DEATH_SOUND, 0.25)
pygame.mixer.Sound.set_volume(SCORE_SOUND, 0.25)

PIPE_SURFACE = pygame.image.load(os.path.join("assets", "pipe_5x.png")).convert_alpha()

GAME_OVER = pygame.image.load(os.path.join("assets", "message-export.png")).convert_alpha()
GAME_OVER_RECT = GAME_OVER.get_rect(center = (WIDTH / 2, HEIGHT / 2))

pipe_list = []
pipe_height = [300,350,400,450,500,550,600]

SPAWNPIPE = pygame.USEREVENT
BIRDFLAP = pygame.USEREVENT + 1

pygame.time.set_timer(SPAWNPIPE, 2000)
pygame.time.set_timer(BIRDFLAP, 200)

def draw_floor():
    screen.blit(FLOOR, (floor_x_pos, HEIGHT - FLOOR_HEIGHT))
    screen.blit(FLOOR, (floor_x_pos + WIDTH, HEIGHT - FLOOR_HEIGHT))

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = PIPE_SURFACE.get_rect(midtop = (WIDTH + 100, random_pipe_pos))
    top_pipe = PIPE_SURFACE.get_rect(midbottom = (WIDTH + 100, random_pipe_pos - 200))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= SCENE_SPEED
    return pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= HEIGHT:
            screen.blit(PIPE_SURFACE, pipe)
        else:
            flip_pipe = pygame.transform.flip(PIPE_SURFACE, False, True)
            screen.blit(flip_pipe, pipe)

def check_collision(pipes):
    for pipe in pipes:
        if BIRD_RECT.colliderect(pipe):
            DEATH_SOUND.play()
            return False

    if BIRD_RECT.top <= 0 or BIRD_RECT.bottom >= HEIGHT - FLOOR_HEIGHT:
        DEATH_SOUND.play()
        return False

    return True

def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, bird_movement * -3 ,1)
    return new_bird

def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center = (BIRD_RECT.centerx, BIRD_RECT.centery))
    return new_bird, new_bird_rect

def score_display(game_state):
    if game_state == "main_game":
        score_surface = game_font.render(str(int(score)), True, (255,255,255))
        score_rect = score_surface.get_rect(center = (WIDTH / 2, 100))
        screen.blit(score_surface, score_rect)

    if game_state == "game_over":
        score_surface = game_font.render(f"Score: {int(score)}", True, (84,56,71))
        score_rect = score_surface.get_rect(topleft = (50, 250))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f"Highscore: {int(highscore)}", True, (84,56,71))
        high_score_rect = high_score_surface.get_rect(topright = (WIDTH - 50, 250))
        screen.blit(high_score_surface, high_score_rect)

pipe_score_index = 0

def increment_score(pipe_list):
    global pipe_score_index, score
    if len(pipe_list) > 2:
        pipex, pipey, pipe2x, pipe2y = pipe_list[int(pipe_score_index)]
        if 280 > pipex:
            score += 1
            SCORE_SOUND.play()
            pipe_score_index += 2

def update_score(score, highscore):
    if score > highscore:
        highscore = score
    return highscore

# Game variables
GRAVITY = 0.25
bird_movement = 0
game_active = False
SCENE_SPEED = 3
score = 0
highscore = 0

floor_x_pos = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 6
                FLAP_SOUND.play()

            if event.key == pygame.K_SPACE and game_active == False:
                game_active = True
                pipe_list.clear()
                BIRD_RECT.center = (300, 480)
                bird_movement = 0
                pipe_score_index = 0
                score = 0

        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())

        if event.type == BIRDFLAP:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0

            BIRD, BIRD_RECT = bird_animation()

    screen.blit(BG, (0,0))

    if game_active:
        # Bird
        bird_movement += GRAVITY
        rotated_bird = rotate_bird(BIRD)
        BIRD_RECT.centery += bird_movement
        screen.blit(rotated_bird, BIRD_RECT)
        game_active = check_collision(pipe_list)

        # Pipes
        move_pipes(pipe_list)
        draw_pipes(pipe_list)

        floor_x_pos -= SCENE_SPEED

        increment_score(pipe_list)

        score_display("main_game")
    
    draw_floor()

    if not game_active:
        screen.blit(GAME_OVER, GAME_OVER_RECT)
        highscore = update_score(score, highscore)
        score_display("game_over")

    if floor_x_pos <= -WIDTH:
        floor_x_pos = 0

    pygame.display.update()
    clock.tick(FPS)
