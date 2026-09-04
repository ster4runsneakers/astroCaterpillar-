# synastry_engine.py - AstroCaterpillar Synastry & Transits Engine
from natal_aspects_engine import ASPECT_TYPES

def calculate_synastry_aspects(pos1: dict, pos2: dict) -> list:
    """Υπολογίζει τις αστρολογικές όψεις μεταξύ δύο γενέθλιων χαρτών (Συναστρία)."""
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



def calculate_monthly_transits(natal_positions: dict, year: int, month: int):
    """
    Υπολογίζει τις σημαντικές διελεύσεις του μήνα σε σχέση με τις γενέθλιες θέσεις.
    Διαχειρίζεται αυτόματα είτε float μοίρες είτε dictionaries της μορφής {'deg': float, ...}.
    """
    # Βοηθητική συνάρτηση για ασφαλή εξαγωγή μοιρών
    def _safe_extract_deg(val):
        if isinstance(val, dict):
            return float(val.get("deg", 0.0))
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    # Καθαρισμός των γενέθλιων μοιρών
    clean_natal = {planet: _safe_extract_deg(pos) for planet, pos in natal_positions.items()}

    # Υπολογισμός διελεύσεων για τη 15η ημέρα του επιλεγμένου μήνα
    transit_raw_positions = calculate_natal_positions(year, month, 15, 12.0)
    clean_transits = {planet: _safe_extract_deg(pos) for planet, pos in transit_raw_positions.items()}

    transits_found = []

    # Σημαντικές όψεις διελεύσεων
    aspect_targets = {
        0.0: "Σύνοδος / Conjunction",
        60.0: "Εξάγωνο / Sextile",
        90.0: "Τετράγωνο / Square",
        120.0: "Τρίγωνο / Trine",
        180.0: "Αντίθεση / Opposition"
    }

    # Έλεγχος αργών & μέσων πλανητών
    outer_planets = ["Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

    for t_planet in outer_planets:
        if t_planet not in clean_transits:
            continue
        
        t_deg = clean_transits[t_planet]

        for n_planet, n_deg in clean_natal.items():
            diff = abs(t_deg - n_deg) % 360.0
            if diff > 180.0:
                diff = 360.0 - diff

            for target_angle, aspect_name in aspect_targets.items():
                # Ανοχή (Orb) 3.0 μοίρες για τις μηνιαίες διελεύσεις
                if abs(diff - target_angle) <= 3.0:
                    transits_found.append({
                        "transit_planet": t_planet,
                        "aspect": aspect_name,
                        "natal_planet": n_planet,
                        "orb": round(abs(diff - target_angle), 2)
                    })

    return transits_found            
            
