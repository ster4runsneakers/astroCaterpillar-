# interpretations_el.py

ZODIAC_SIGNS_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer", 
    "Leo", "Virgo", "Libra", "Scorpio", 
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_sign_from_degrees(deg: float):
    """
    Μετατρέπει τις μοίρες (0° - 360°) στο αντίστοιχο Ζώδιο 
    και την εσωτερική μοίρα του ζωδίου (0° - 29.99°).
    """
    normalized_deg = deg % 360.0
    sign_index = int(normalized_deg // 30)
    degree_in_sign = normalized_deg % 30.0
    
    sign_name = ZODIAC_SIGNS_ORDER[sign_index]
    return sign_name, degree_in_sign
  
