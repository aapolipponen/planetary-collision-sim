from planet import sun, bodies, reset_bodies, earth, mars
from constants import day, hour, minute, second
import pygame
import numpy as np
from simulation import run_simulation
from display import draw_objects, display_time

focus_object = earth

FULL_ORBITS = True

star_size_multiplier = 1
planet_size_multiplier = 1
moon_size_multiplier = 1

# Define the initial timescale value in seconds
timescale_seconds = second * 50

# Calculate scaling factors for size and distance
SCALE_DIST = 2e-5

ZOOM_SPEED = 1e-9  # Adjust this value to increase/decrease the zoom speed

def update_timescale(timescale_seconds, direction, speed=hour):
    if direction == 'up':
        return timescale_seconds * (speed)
    elif direction == 'down':
        return timescale_seconds / (speed)
    else:
        return timescale_seconds

def calculate_distance(pos1, pos2):
    return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

def find_closest_body(pos, bodies, SCALE_DIST, focus_object):
    closest_body = None
    min_distance = float('inf')
    focus_pos_pygame = np.array([pygame.display.get_surface().get_width() // 2, pygame.display.get_surface().get_height() // 2])

    for body in bodies:
        body_pos_scaled = (body.pos[:2] - focus_object.pos[:2]) * SCALE_DIST
        body_pos_pygame = focus_pos_pygame + body_pos_scaled
        distance = calculate_distance(pos, body_pos_pygame)

        if distance < min_distance:
            min_distance = distance
            closest_body = body

    return closest_body

# Main simulation loop
running = True
paused = False
while running:
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:  # shift is pressed
                if event.button == 4:  # scroll up
                    timescale_seconds = update_timescale(timescale_seconds, 'up')
                elif event.button == 5:  # scroll down
                    timescale_seconds = update_timescale(timescale_seconds, 'down') 
            elif event.button == 4:  # scroll up
                SCALE_DIST += ZOOM_SPEED
            elif event.button == 5:  # scroll down
                SCALE_DIST -= ZOOM_SPEED
            elif event.button == 1:
                pos = pygame.mouse.get_pos()
                closest_body = find_closest_body(pos, bodies, SCALE_DIST, focus_object)
                if closest_body is not None:
                    focus_object = closest_body
        elif event.type == pygame.KEYDOWN:
            # Space key pauses the game
            if event.key == pygame.K_SPACE:
                paused = not paused  # Toggle paused state        
        elif event.type == pygame.QUIT:
            running = False

    if not paused:
        for body in bodies:
            run_simulation(timescale_seconds)
    
    draw_objects(focus_object, SCALE_DIST, star_size_multiplier, planet_size_multiplier, moon_size_multiplier)
    display_time(timescale_seconds)
    pygame.display.flip()
    pygame.time.wait(10)
     
pygame.quit()
