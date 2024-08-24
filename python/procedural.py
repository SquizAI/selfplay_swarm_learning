import random

def generate_planet():
    planets = ["Zeta-12", "Orion-7", "Nebula-X", "Vortex-4"]
    return {"planet": random.choice(planets), "resources": ["Gold", "Helium", "Platinum"]}
