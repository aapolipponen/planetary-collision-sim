import numpy as np
from constants import G

def fibonacci_sphere(samples=1):
    points = []
    phi = np.pi * (3. - np.sqrt(5.))  # golden angle in radians

    for i in range(samples):
        y = 1 - (i / float(samples - 1)) * 2  # y goes from 1 to -1
        radius = np.sqrt(1 - y*y)  # radius at y

        theta = phi * i  # golden angle increment

        x = np.cos(theta) * radius
        z = np.sin(theta) * radius

        points.append((x, y, z))

    return points

class Part:
    def __init__(self, pos, vel, radius, mass):
        self.pos = pos
        self.vel = vel
        self.radius = radius
        self.mass = mass

class body:
    density_factor = 0.01  # Class variable, shared among all instances of the class

    def __init__(self, name, pos, mass, radius, color, type, parent=None, velocity=np.array([0.0, 0.0, 0.0])):
        self.name = name
        self.pos = np.array(pos)
        self.radius = radius
        self.color = color
        self.type = type
        self.parent = parent
        self.vel = np.array(velocity)
        self.parts = self.generate_parts(mass) if self.type != "star" else []

    def generate_parts(self, total_mass):
        volume = 4/3 * np.pi * self.radius**3  # Volume of the body
        density = total_mass / volume  # Density of the body
        num_parts = max(1, int(density * body.density_factor))  # Use the class variable density_factor
        part_mass = total_mass / num_parts
        part_radius = self.radius / num_parts**(1/3)  # Assume parts are uniform and fill the body

        # Use the fibonacci_sphere function to generate part positions
        part_positions = fibonacci_sphere(num_parts)
        parts = []
        for pos in part_positions:
            # Randomly adjust the radius of each position and scale by the body radius
            r = np.random.uniform(0, 1)
            part_pos = self.pos + np.array(pos) * self.radius * r
            part = Part(part_pos, self.vel, part_radius, part_mass)
            parts.append(part)
        
        return parts

    # Add a method to calculate the mass
    def mass(self):
        return sum(part.mass for part in self.parts)
