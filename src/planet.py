from constants import AU, km
import numpy as np
from body import body

sun = body(
    name="Sun",
    pos=[0.0, 0.0, 0.0],
    mass=1.989 * 10**30,
    radius=696342 * km,
    color=[255, 223, 0],
    type="star",
    parent=None,
)

earth = body(
    name="Earth",                                                 
    pos=[1.0 * AU, 0.0, 0.0],
    mass=5.97219 * 10**24,                                       
    radius=6371 * km,                                             
    color=[0, 0, 255],                                           
    type="planet",                                                
    parent=sun,                                             
    velocity=[0, -10.001 * km, 0]  # Reduced velocity
)

mars = body(
    name="Mars",
    pos=[1.0001 * AU, 0.0, 0.0],  # Very close to Earth
    mass=6.4171 * 10**23,
    radius=3389.5 * km,
    color=[255, 0, 0],
    type="planet",
    parent=sun,
    velocity=[0, -10.0 * km, 0]  # Slightly higher velocity than Earth
)

def reset_bodies():
    for body in bodies:
        body.reset()

bodies = [sun, earth, mars]