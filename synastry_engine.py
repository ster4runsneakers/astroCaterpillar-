# synastry_engine.py - Calculation Engine for Synastry & Transits
import math
from ephemeris_engine import calculate_natal_positions

def calculate_synastry_aspects(pos1: dict, pos2: dict):
    """
    Υπολογίζει τις όψεις συναστρίας μεταξύ δύο ατόμων.
    """
    def _safe_extract_deg(val):
        if isinstance(val, dict):
            return float(val.get("deg", 0.0))
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    clean_pos1 = {p: _safe_extract_deg(v) for p, v in pos1.items()}
    clean_pos2 = {p: _safe_extract_deg(v) for p, v in pos2.items()}

    aspect_targets = {
        0.0: ("Σύνοδος / Conjunction", 6.0),
        60.0: ("Εξάγωνο / Sextile", 4.0),
        90.0: ("Τετράγωνο / Square", 5.0),
        120.0: ("Τρίγωνο / Trine", 5.0),
        180.0: ("Αντίθεση / Opposition", 6.0)
    }

    synastry_aspects = []

    for p1_name, deg1 in clean_pos1.items():
        for p2_name, deg2 in clean_pos2.items():
            diff = abs(deg1 - deg2) % 360.0
            if diff > 180.0:
                diff = 360.0 - diff

            for target_angle, (aspect_name, max_orb) in aspect_targets.items():
                orb = abs(diff - target_angle)
                if orb <= max_orb:
                    synastry_aspects.append({
                        "p1": p1_name,
                        "p2": p2_name,
                        "aspect": aspect_name,
                        "orb": round(orb, 2)
                    })

    return synastry_aspects


def calculate_monthly_transits(natal_positions: dict, year: int, month: int):
    """
    Υπολογίζει τις σημαντικές διελεύσεις του μήνα σε σχέση με τις γενέθλιες θέσεις.
    """
    def _safe_extract_deg(val):
        if isinstance(val, dict):
            return float(val.get("deg", 0.0))
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    clean_natal = {planet: _safe_extract_deg(pos) for planet, pos in natal_positions.items()}

    aspect_targets = {
        0.0: "Σύνοδος / Conjunction",
        60.0: "Εξάγωνο / Sextile",
        90.0: "Τετράγωνο / Square",
        120.0: "Τρίγωνο / Trine",
        180.0: "Αντίθεση / Opposition"
    }
    outer_planets = ["Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    sample_days = [1, 8, 15, 22, 28]
    seen = set()
    transits_found = []

    for day in sample_days:
        try:
            transit_raw_positions = calculate_natal_positions(year, month, day, 12.0)
        except Exception:
            continue
        clean_transits = {planet: _safe_extract_deg(pos) for planet, pos in transit_raw_positions.items()}
        for t_planet in outer_planets:
            if t_planet not in clean_transits:
                continue
            t_deg = clean_transits[t_planet]
            for n_planet, n_deg in clean_natal.items():
                diff = abs(t_deg - n_deg) % 360.0
                if diff > 180.0:
                    diff = 360.0 - diff
                for target_angle, aspect_name in aspect_targets.items():
                    if abs(diff - target_angle) <= 3.0:
                        key = (t_planet, aspect_name, n_planet)
                        if key in seen:
                            continue
                        seen.add(key)
                        transits_found.append({
                            "transit_planet": t_planet,
                            "aspect": aspect_name,
                            "natal_planet": n_planet,
                            "orb": round(abs(diff - target_angle), 2),
                            "approx_day": day,
                        })
    return transits_found
