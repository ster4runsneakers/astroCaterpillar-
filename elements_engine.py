# elements_engine.py

ELEMENTS_MAP = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}

MODALITIES_MAP = {
    "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable"
}

def calculate_elements_and_modalities(positions_signs: dict):
    elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    modalities = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    total = len(positions_signs)

    for planet, sign in positions_signs.items():
        elem = ELEMENTS_MAP.get(sign)
        mod = MODALITIES_MAP.get(sign)
        if elem:
            elements[elem] += 1
        if mod:
            modalities[mod] += 1

    elem_pct = {k: round((v / total) * 100, 1) for k, v in elements.items()} if total > 0 else elements
    mod_pct = {k: round((v / total) * 100, 1) for k, v in modalities.items()} if total > 0 else modalities

    return elem_pct, mod_pct
  
