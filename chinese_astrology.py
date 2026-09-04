# chinese_astrology.py

ANIMALS = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]

def get_chinese_zodiac(year: int) -> dict:
    base_year = 1900  # 1900 was Metal Rat
    offset = year - base_year
    
    animal = ANIMALS[offset % 12]
    element = ELEMENTS[((year - 4) % 10) // 2]
    
    return {"animal": animal, "element": element}
  
