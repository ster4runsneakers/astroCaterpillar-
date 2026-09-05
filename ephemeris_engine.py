# ephemeris_engine.py - AstroCaterpillar Ephemeris Engine with Retrograde Detection
import datetime
import math

PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

def julian_day(year: int, month: int, day: int, hour_decimal: float) -> float:
    if month <= 2:
        year -= 1
        month += 12
    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5
    jd += hour_decimal / 24.0
    return jd

def get_planet_raw_deg(planet_name: str, T: float) -> float:
    if planet_name == "Sun":
        L0 = 280.46646 + 36000.76983 * T
        M = 357.52911 + 35999.05029 * T
        C = (1.914602 - 0.004817 * T) * math.sin(math.radians(M)) + (0.019993 - 0.000101 * T) * math.sin(math.radians(2 * M))
        return (L0 + C) % 360.0

    elif planet_name == "Moon":
        L = 218.316 + 13.176396 * (T * 36525)
        M = 134.963 + 13.064993 * (T * 36525)
        F = 93.272 + 13.229350 * (T * 36525)
        deg = L + 6.289 * math.sin(math.radians(M)) - 1.274 * math.sin(math.radians(M - 2 * (L - 280.466))) + 0.658 * math.sin(math.radians(2 * (L - 280.466)))
        return deg % 360.0

    speeds = {
        "Mercury": 4.15201, "Venus": 1.62549, "Mars": 0.52402,
        "Jupiter": 0.08308, "Saturn": 0.03346, "Uranus": 0.01173,
        "Neptune": 0.00598, "Pluto": 0.00396
    }
    base_deg = {
        "Mercury": 252.25, "Venus": 181.98, "Mars": 355.45,
        "Jupiter": 34.40, "Saturn": 50.08, "Uranus": 314.05,
        "Neptune": 304.35, "Pluto": 238.92
    }
    days = T * 36525.0
    sp = speeds.get(planet_name, 0.1)
    b = base_deg.get(planet_name, 0.0)
    
    # Προσθήκη ημιτονοειδούς διακύμανσης για προσομοίωση φαινόμενης ανάδρομης κίνησης
    retro_phase = math.sin(math.radians(days * sp * 0.5)) * 6.0
    deg = b + days * sp + retro_phase
    return deg % 360.0

def calculate_natal_positions(year: int, month: int, day: int, hour_decimal: float) -> dict:
    """Υπολογίζει τις μοίρες και αν ο πλανήτης είναι ανάδρομος (is_retrograde)."""
    jd = julian_day(year, month, day, hour_decimal)
    T = (jd - 2451545.0) / 36525.0
    T_next = T + (1.0 / 36525.0) # 1 ημέρα μετά για έλεγχο ταχύτητας
    
    positions = {}
    for p in PLANETS:
        deg = get_planet_raw_deg(p, T)
        deg_next = get_planet_raw_deg(p, T_next)
        
        # Αν η μοίρα μειώνεται, ο πλανήτης είναι ανάδρομος
        diff = (deg_next - deg) % 360.0
        is_retro = True if (diff > 180.0 or diff < 0) and p not in ["Sun", "Moon"] else False
        
        positions[p] = {
            "deg": round(deg, 2),
            "is_retro": is_retro
        }
    return positions

import swisseph as swe

def calculate_houses(year, month, day, utc_hour, lat, lon):
    """
    Υπολογισμός Οίκων & Ωροσκόπου με το Swiss Ephemeris.
    - year, month, day: Ημερομηνία γέννησης
    - utc_hour: Ώρα σε UTC (float)
    - lat: Γεωγραφικό Πλάτος (π.χ. 37.9838 για Αθήνα)
    - lon: Γεωγραφικό Μήκος (π.χ. 23.7275 για Αθήνα)
    """
    # 1. Υπολογισμός Julian Day σε Universal Time
    jul_day = swe.julday(year, month, day, utc_hour)
    
    # 2. Υπολογισμός Οίκων (Placidus system = 'P')
    # ΠΡΟΣΟΧΗ: Η σειρά είναι (jul_day, lat, lon, house_system)
    houses_cusps, ascmc = swe.houses(jul_day, lat, lon, b'P')
    
    # ascmc[0] = Ascendant (Ωροσκόπος)
    asc_deg = ascmc[0]
    
    houses_dict = {}
    for i in range(12):
        houses_dict[f"House_{i+1}"] = houses_cusps[i]
        
    # Ο 1ος Οίκος ταυτίζεται με τον Ωροσκόπο
    houses_dict["House_1"] = asc_deg
    
    return houses_dict
