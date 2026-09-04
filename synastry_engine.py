# synastry_engine.py
from natal_aspects_engine import ASPECT_TYPES

def calculate_synastry_aspects(pos1: dict, pos2: dict) -> list:
    aspects = []
    for p1, deg1 in pos1.items():
        for p2, deg2 in pos2.items():
            diff = abs(deg1 - deg2) % 360.0
            if diff > 180:
                diff = 360.0 - diff

            for aspect_name, data in ASPECT_TYPES.items():
                target_angle = data["angle"]
                orb = data["orb"]
                if abs(diff - target_angle) <= orb:
                    aspects.append({
                        "p1": f"Person1_{p1}",
                        "p2": f"Person2_{p2}",
                        "aspect": aspect_name,
                        "orb": round(abs(diff - target_angle), 2)
                    })
    return aspects
  
