import pygame
import numpy as np
from planet import bodies
from constants import half_rgb, year, month, day, hour, minute

# Initialize Pygame and set up the display window
pygame.init()

screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)

# Dictionary to hold planet trails
planet_trails = {body.name: [] for body in bodies}

def convert_seconds_to_human_readable(seconds):
    # Determine if input is negative
    is_negative = seconds < 0
    seconds = abs(seconds)  # Use absolute value for calculations
    
    years, seconds = divmod(seconds, year)
    months, seconds = divmod(seconds, month)
    days, seconds = divmod(seconds, day)
    hours, seconds = divmod(seconds, hour)
    minutes, seconds = divmod(seconds, minute)
    
    # If input was negative, add negative sign to output
    if is_negative:
        return -int(years), -int(months), -int(days), -int(hours), -int(minutes), -int(seconds)
    else:
        return int(years), int(months), int(days), int(hours), int(minutes), int(seconds)
    
def display_time(timescale):
    try:
        seconds = timescale
        years, months, days, hours, minutes, seconds = convert_seconds_to_human_readable(seconds)
        human_readable_time = f"Time: {years}y {months}m {days}d {hours}h {minutes}m {seconds}s"
        font = pygame.font.Font(None, 36)
        text = font.render(human_readable_time, 1, (255, 255, 255))
        screen.blit(text, (50,50))
    except Exception as e:
        if "termux" in str(e).lower():
            print("Running on Termux, skipping text rendering!")
        else:
            raise e
        
def draw_trail(screen, body, planet_trails, focus_object, SCALE_DIST):
    focus_pos_pygame = np.array([screen.get_width() // 2, screen.get_height() // 2])

    # Store the scaled position in trail
    planet_trails[body.name].append((body.pos[:2] - focus_object.pos[:2]))

    # If not displaying full orbits, remove the oldest position if the trail is too long
    if len(planet_trails[body.name]) > 100:
        planet_trails[body.name].pop(0)

    # Draw the trail with a fixed color
    for i in range(1, len(planet_trails[body.name])):
        # Calculate a fade factor based on the position in the trail
        fade_factor = i / len(planet_trails[body.name])
        trail_color = tuple([int(c * fade_factor) for c in body.color])

        trail_start = (planet_trails[body.name][i-1] * SCALE_DIST + focus_pos_pygame).astype(int)
        trail_end = (planet_trails[body.name][i] * SCALE_DIST + focus_pos_pygame).astype(int)

        pygame.draw.line(screen, trail_color, tuple(trail_start), tuple(trail_end))

def draw_path(screen, body, SCALE_DIST):
    focus_pos_pygame = np.array([screen.get_width() // 2, screen.get_height() // 2])

    # Assuming the body moves in a straight line, calculate the next position after a fixed number of time steps
    num_steps = 1000
    positions = [body.pos[:2] + i * body.vel[:2] for i in range(num_steps)]

    # Scale and translate the coordinates
    x_pygame = (np.array([pos[0] for pos in positions]) * SCALE_DIST + focus_pos_pygame[0]).astype(int)
    y_pygame = (np.array([pos[1] for pos in positions]) * SCALE_DIST + focus_pos_pygame[1]).astype(int)

    # Draw the path
    for i in range(1, len(x_pygame)):
        pygame.draw.line(screen, half_rgb(body.color), (x_pygame[i-1], y_pygame[i-1]), (x_pygame[i], y_pygame[i]))

def draw_objects(focus_object, SCALE_DIST, star_size_multiplier, planet_size_multiplier, moon_size_multiplier):
    focus_pos_pygame = np.array([screen.get_width() // 2, screen.get_height() // 2])
    screen.fill((0, 0, 0))

    for body in bodies:
        
        print(f"Drawing {body.name} at position {body.pos} with radius {body.radius} vel {body.vel}")
        
        if body.parent == None:
            draw_path(screen, body, SCALE_DIST)
        else:
            draw_trail(screen, body, planet_trails, focus_object, SCALE_DIST)

        # Calculate the planet's position relative to the focus object
        planet_pos_scaled = (body.pos[:2] - focus_object.pos[:2]) * SCALE_DIST
        planet_pos_pygame = focus_pos_pygame + planet_pos_scaled

        # Choose the size multiplier based on the object type
        if body.type == 'star':
            size_multiplier = star_size_multiplier
        elif body.type == 'planet':
            size_multiplier = planet_size_multiplier
        elif body.type == 'moon':
            size_multiplier = moon_size_multiplier
        else:
            size_multiplier = 1  # Default multiplier

        # Draw the body only if it's a star
        if body.type == 'star':
            planet_radius = max(1, int(body.radius * SCALE_DIST * size_multiplier))
            pygame.draw.circle(screen, body.color, tuple(planet_pos_pygame.astype(int)), planet_radius)
        
        # Draw the parts only if the body is not a star
        if body.type != 'star':
            for part in body.parts:
                # Calculate the part's position relative to the focus object
                part_pos_scaled = (part.pos[:2] - focus_object.pos[:2]) * SCALE_DIST
                part_pos_pygame = focus_pos_pygame + part_pos_scaled

                # Calculate the part's radius in pixels
                part_radius = max(1, int(part.radius * SCALE_DIST * size_multiplier))

                # Draw the part
                pygame.draw.circle(screen, body.color, tuple(part_pos_pygame.astype(int)), part_radius)
