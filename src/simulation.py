from constants import G, k
from planet import bodies
import numpy as np
from body import body
from multiprocessing import Pool

def calculate_net_force_wrapper(args):
    return calculate_net_force(*args)

def calculate_net_force(target_body):
    net_force = np.array([0.0, 0.0, 0.0])
    for body in bodies:
        if body != target_body:
            r = body.pos - target_body.pos
            r_mag = np.linalg.norm(r)
            if r_mag == 0:  # bodies are at the same position
                continue
            force_mag = G * target_body.mass() * body.mass() / r_mag**2
            force = force_mag * r / r_mag
            net_force += force
    return net_force

def calculate_net_force_on_part_wrapper(args):
    return calculate_net_force_on_part(*args)

def calculate_net_force_on_part(target_part, all_parts):
    restitution = 0.2  # Partially inelastic collisions
    
    net_force = np.array([0.0, 0.0, 0.0])
    for part in all_parts:
        if part != target_part:
            r = part.pos - target_part.pos
            r_mag = np.linalg.norm(r)
            if r_mag == 0:  # parts are at the same position
                continue
            
            force_mag = G * target_part.mass * part.mass / r_mag**2
            
            force = force_mag * r / r_mag
            net_force += force

            # Impulse-based collision response
            overlap = part.radius + target_part.radius - r_mag
            if overlap > 0:  # if there is a collision
                normal = r / r_mag  # normal vector
                relative_velocity = target_part.vel - part.vel
                impulse_magnitude = -(1 + restitution) * np.dot(relative_velocity, normal) / (1/target_part.mass + 1/part.mass)
                impulse = impulse_magnitude * normal

                # Apply the impulse
                target_part.vel += impulse / target_part.mass
                part.vel -= impulse / part.mass

    return net_force
def run_simulation(timescale_seconds):
    bodies_copy = bodies[:]
    all_parts = [part for body in bodies_copy for part in body.parts]
    restitution = 0.2  # Partially inelastic collisions

    # Create a pool of worker processes for bodies
    with Pool() as pool:
        # Calculate forces on bodies in parallel
        forces = pool.map(calculate_net_force_wrapper, [(body,) for body in bodies_copy])

    for body, force in zip(bodies_copy, forces):
        acceleration = force / body.mass()
        if body.name != "Sun":
            body.vel += 0.5 * acceleration * timescale_seconds

        body.pos += body.vel * timescale_seconds

        # Create a pool of worker processes for parts
        with Pool() as pool:
            # Calculate forces on parts in parallel
            part_forces = pool.map(calculate_net_force_on_part_wrapper, [(part, all_parts) for part in body.parts])

        for part, force in zip(body.parts, part_forces):
            # Update velocities and positions of parts
            acceleration = force / part.mass
            part.vel += 0.5 * acceleration * timescale_seconds
            part.pos += part.vel * timescale_seconds

    # Check for collisions and resolve them
    for i in range(len(all_parts)):
        for j in range(i + 1, len(all_parts)):
            part1 = all_parts[i]
            part2 = all_parts[j]
            r = part2.pos - part1.pos
            r_mag = np.linalg.norm(r)
            overlap = part1.radius + part2.radius - r_mag
            if overlap > 0:  # if there is a collision
                normal = r / r_mag  # normal vector
                relative_velocity = part1.vel - part2.vel
                impulse_magnitude = -(1 + restitution) * np.dot(relative_velocity, normal) / (1/part1.mass + 1/part2.mass)
                impulse = impulse_magnitude * normal

                # Apply the impulse
                part1.vel += impulse / part1.mass
                part2.vel -= impulse / part2.mass

    # Repeat for second half-step velocity update
    with Pool() as pool:
        forces = pool.map(calculate_net_force_wrapper, [(body,) for body in bodies])

    for body, force in zip(bodies, forces):
        acceleration = force / body.mass()
        if body.name != "Sun":
            body.vel += 0.5 * acceleration * timescale_seconds

        # Create a pool of worker processes for parts
        with Pool() as pool:
            # Calculate forces on parts in parallel
            part_forces = pool.map(calculate_net_force_on_part_wrapper, [(part, all_parts) for part in body.parts])

        for part, force in zip(body.parts, part_forces):
            # Second half-step velocity update for parts
            acceleration = force / part.mass
            part.vel += 0.5 * acceleration * timescale_seconds