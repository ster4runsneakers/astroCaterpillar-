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


def calculate_monthly_transits(natal_positions: dict, year: int, month: int) -> list:
    """
    Υπολογίζει τις μηνιαίες διελεύσεις εστιάζοντας στους μακρο-κύκλους (αργοί πλανήτες)
    και διαχωρίζοντας τους γρήγορους πλανήτες ως triggers.
    """
    from ephemeris_engine import calculate_natal_positions
    
    # Υπολογισμός πλανητικών θέσεων στα μέσα του μήνα (15η ημέρα, 12:00)
    mid_month_positions = calculate_natal_positions(year, month, 15, 12.0)
    
    outer_planets = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Mars"]
    transits = []
    
    for t_planet, t_deg in mid_month_positions.items():
        for n_planet, n_deg in natal_positions.items():
            diff = abs(t_deg - n_deg) % 360.0
            if diff > 180:
                diff = 360.0 - diff
                
            # Αυστηρότερο Orb: 5° για αργούς πλανήτες (Macro), 2° για γρήγορους (Trigger)
            max_orb = 5.0 if t_planet in outer_planets else 2.0
            
            for aspect_name, data in ASPECT_TYPES.items():
                target_angle = data["angle"]
                if abs(diff - target_angle) <= max_orb:
                    transits.append({
                        "transit_planet": t_planet,
                        "natal_planet": n_planet,
                        "aspect": aspect_name,
                        "orb": round(abs(diff - target_angle), 2),
                        "type": "Macro" if t_planet in outer_planets else "Trigger"
                    })
    return transits
