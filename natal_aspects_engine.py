# natal_aspects_engine.py

ASPECT_TYPES = {
    "Conjunction": {"angle": 0, "orb": 8},
    "Opposition": {"angle": 180, "orb": 8},
    "Trine": {"angle": 120, "orb": 8},
    "Square": {"angle": 90, "orb": 7},
    "Sextile": {"angle": 60, "orb": 6}
}

def calculate_natal_aspects(positions: dict) -> list:
    aspects = []
    planets = list(positions.keys())

    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1, p2 = planets[i], planets[j]
            deg1, deg2 = positions[p1], positions[p2]
            
            diff = abs(deg1 - deg2) % 360.0
            if diff > 180:
                diff = 360.0 - diff

            for aspect_name, data in ASPECT_TYPES.items():
                target_angle = data["angle"]
                orb = data["orb"]
                if abs(diff - target_angle) <= orb:
                    aspects.append({
                        "p1": p1,
                        "p2": p2,
                        "aspect": aspect_name,
                        "orb": round(abs(diff - target_angle), 2)
                    })
    return aspects
  
