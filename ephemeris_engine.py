# ephemeris_engine.py
import datetime

PLANET_SPEEDS = {
    "Sun": 0.9856,
    "Moon": 13.1763,
    "Mercury": 1.2000,
    "Venus": 1.6000,
    "Mars": 0.5240,
    "Jupiter": 0.0831,
    "Saturn": 0.0335,
    "Uranus": 0.0117,
    "Neptune": 0.0060,
    "Pluto": 0.0040
}

BASE_POSITIONS = {
    "Sun": 280.46,
    "Moon": 218.32,
    "Mercury": 252.25,
    "Venus": 181.98,
    "Mars": 355.43,
    "Jupiter": 34.35,
    "Saturn": 50.08,
    "Uranus": 314.05,
    "Neptune": 304.35,
    "Pluto": 238.92
}

def _days_since_j2000(year: int, month: int, day: int, hour_decimal: float) -> float:
    d = datetime.date(year, month, day)
    epoch = datetime.date(2000, 1, 1)
    diff_days = (d - epoch).days
    return diff_days + (hour_decimal - 12.0) / 24.0

def calculate_natal_positions(year: int, month: int, day: int, hour_decimal: float) -> dict:
    """Υπολογίζει τις μοίρες των πλανητών (0° - 360°)."""
    days = _days_since_j2000(year, month, day, hour_decimal)
    positions = {}
    for planet, speed in PLANET_SPEEDS.items():
        base = BASE_POSITIONS[planet]
        deg = (base + speed * days) % 360.0
        if deg < 0:
            deg += 360.0
        positions[planet] = round(deg, 2)
    return positions

def calculate_houses(year: int, month: int, day: int, hour_decimal: float, lat: float, lon: float) -> dict:
    """Υπολογίζει τις αιχμές των 12 Οίκων (Equal House System)."""
    days = _days_since_j2000(year, month, day, hour_decimal)
    lst = (100.46 + 0.985647 * days + lon + hour_decimal * 15.0) % 360.0
    ascendant = (lst + 90.0) % 360.0
    houses = {}
    for i in range(1, 13):
        house_deg = (ascendant + (i - 1) * 30.0) % 360.0
        houses[f"House_{i}"] = round(house_deg, 2)
    return houses
  
