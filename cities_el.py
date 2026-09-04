# cities_el.py - AstroCaterpillar Cities & Translation Engine

GREEK_AND_WORLD_CITIES = {
    # --- ΕΛΛΑΔΑ & ΚΥΠΡΟΣ ---
    "Athens": {"lat": 37.9838, "lon": 23.7275, "el": "Αθήνα", "en": "Athens"},
    "Thessaloniki": {"lat": 40.6401, "lon": 22.9444, "el": "Θεσσαλονίκη", "en": "Thessaloniki"},
    "Patras": {"lat": 38.2466, "lon": 21.7345, "el": "Πάτρα", "en": "Patras"},
    "Heraklion": {"lat": 35.3387, "lon": 25.1442, "el": "Ηράκλειο", "en": "Heraklion"},
    "Larissa": {"lat": 39.6390, "lon": 22.4191, "el": "Λάρισα", "en": "Larissa"},
    "Volos": {"lat": 39.3621, "lon": 22.9422, "el": "Βόλος", "en": "Volos"},
    "Ioannina": {"lat": 39.6650, "lon": 20.8537, "el": "Ιωάννινα", "en": "Ioannina"},
    "Chania": {"lat": 35.5138, "lon": 24.0180, "el": "Χανιά", "en": "Chania"},
    "Rhodus": {"lat": 36.4349, "lon": 28.2176, "el": "Ρόδος", "en": "Rhodes"},
    "Alexandroupoli": {"lat": 40.8457, "lon": 25.8739, "el": "Αλεξανδρούπολη", "en": "Alexandroupoli"},
    "Kalamata": {"lat": 37.0422, "lon": 22.1142, "el": "Καλαμάτα", "en": "Kalamata"},
    "Kavala": {"lat": 40.9396, "lon": 24.4069, "el": "Καβάλα", "en": "Kavala"},
    "Corfu": {"lat": 39.6243, "lon": 19.9217, "el": "Κέρκυρα", "en": "Corfu"},
    "Nicosia": {"lat": 35.1856, "lon": 33.3823, "el": "Λευκωσία", "en": "Nicosia"},
    "Limassol": {"lat": 34.6786, "lon": 33.0413, "el": "Λεμεσός", "en": "Limassol"},

    # --- ΡΩΣΙΑ (18 ΠΟΛΕΙΣ) ---
    "Moscow": {"lat": 55.7558, "lon": 37.6173, "el": "Μόσχα (Ρωσία)", "en": "Moscow (Russia)"},
    "Saint Petersburg": {"lat": 59.9343, "lon": 30.3351, "el": "Αγία Πετρούπολη (Ρωσία)", "en": "Saint Petersburg (Russia)"},
    "Novosibirsk": {"lat": 55.0084, "lon": 82.9357, "el": "Νοβοσιμπίρσκ (Ρωσία)", "en": "Novosibirsk (Russia)"},
    "Yekaterinburg": {"lat": 56.8389, "lon": 60.6057, "el": "Εκατερινμπουργκ (Ρωσία)", "en": "Yekaterinburg (Russia)"},
    "Kazan": {"lat": 55.8304, "lon": 49.0661, "el": "Καζάν (Ρωσία)", "en": "Kazan (Russia)"},
    "Nizhny Novgorod": {"lat": 56.2965, "lon": 43.9361, "el": "Νίζνι Νόβγκοροντ (Ρωσία)", "en": "Nizhny Novgorod (Russia)"},
    "Chelyabinsk": {"lat": 55.1644, "lon": 61.4368, "el": "Τσελιάμπινσκ (Ρωσία)", "en": "Chelyabinsk (Russia)"},
    "Samara": {"lat": 53.1959, "lon": 50.1002, "el": "Σαμάρα (Ρωσία)", "en": "Samara (Russia)"},
    "Omsk": {"lat": 54.9885, "lon": 73.3242, "el": "Ομσκ (Ρωσία)", "en": "Omsk (Russia)"},
    "Rostov-on-Don": {"lat": 47.2357, "lon": 39.7015, "el": "Ροστόφ στον Ντον (Ρωσία)", "en": "Rostov-on-Don (Russia)"},
    "Ufa": {"lat": 54.7388, "lon": 55.9721, "el": "Ούφα (Ρωσία)", "en": "Ufa (Russia)"},
    "Krasnoyarsk": {"lat": 56.0153, "lon": 92.8932, "el": "Κρασνογιάρσκ (Ρωσία)", "en": "Krasnoyarsk (Russia)"},
    "Voronezh": {"lat": 51.6755, "lon": 39.2089, "el": "Βορονέζ (Ρωσία)", "en": "Voronezh (Russia)"},
    "Perm": {"lat": 58.0105, "lon": 56.2502, "el": "Περμ (Ρωσία)", "en": "Perm (Russia)"},
    "Volgograd": {"lat": 48.7080, "lon": 44.5133, "el": "Βολγκογκράντ (Ρωσία)", "en": "Volgograd (Russia)"},
    "Krasnodar": {"lat": 45.0355, "lon": 38.9753, "el": "Κρασνοντάρ (Ρωσία)", "en": "Krasnodar (Russia)"},
    "Arkhangelsk": {"lat": 64.5472, "lon": 40.5404, "el": "Αρχάγγελσκ (Ρωσία)", "en": "Arkhangelsk (Russia)"},
    "Vladivostok": {"lat": 43.1155, "lon": 131.8855, "el": "Βλαδιβοστόκ (Ρωσία)", "en": "Vladivostok (Russia)"},

    # --- ΔΙΕΘΝΕΙΣ ΠΟΛΕΙΣ ---
    "London": {"lat": 51.5074, "lon": -0.1278, "el": "Λονδίνο (ΗΒ)", "en": "London (UK)"},
    "New York": {"lat": 40.7128, "lon": -74.0060, "el": "Νέα Υόρκη (ΗΠΑ)", "en": "New York (USA)"},
    "Paris": {"lat": 48.8566, "lon": 2.3522, "el": "Παρίσι (Γαλλία)", "en": "Paris (France)"},
    "Berlin": {"lat": 52.5200, "lon": 13.4050, "el": "Βερολίνο (Γερμανία)", "en": "Berlin (Germany)"},
    "Rome": {"lat": 41.9028, "lon": 12.4964, "el": "Ρώμη (Ιταλία)", "en": "Rome (Italy)"},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503, "el": "Τόκιο (Ιαπωνία)", "en": "Tokyo (Japan)"},
    "Sydney": {"lat": -33.8688, "lon": 151.2093, "el": "Σίδνεϊ (Αυστραλία)", "en": "Sydney (Australia)"}
}

# --- ΔΙΓΛΩΣΣΑ ΛΕΞΙΚΑ ΑΣΤΡΟΛΟΓΙΑΣ ---
ZODIAC_SIGNS = {
    "Aries": {"el": "Κριός", "en": "Aries"},
    "Taurus": {"el": "Ταύρος", "en": "Taurus"},
    "Gemini": {"el": "Δίδυμοι", "en": "Gemini"},
    "Cancer": {"el": "Καρκίνος", "en": "Cancer"},
    "Leo": {"el": "Λέων", "en": "Leo"},
    "Virgo": {"el": "Παρθένος", "en": "Virgo"},
    "Libra": {"el": "Ζυγός", "en": "Libra"},
    "Scorpio": {"el": "Σκορπιός", "en": "Scorpio"},
    "Sagittarius": {"el": "Τοξότης", "en": "Sagittarius"},
    "Capricorn": {"el": "Αιγόκερως", "en": "Capricorn"},
    "Aquarius": {"el": "Υδροχόος", "en": "Aquarius"},
    "Pisces": {"el": "Ιχθύες", "en": "Pisces"}
}

PLANET_TRANSLATIONS = {
    "Sun": {"el": "Ήλιος", "en": "Sun"},
    "Moon": {"el": "Σελήνη", "en": "Moon"},
    "Mercury": {"el": "Ερμής", "en": "Mercury"},
    "Venus": {"el": "Αφροδίτη", "en": "Venus"},
    "Mars": {"el": "Άρης", "en": "Mars"},
    "Jupiter": {"el": "Δίας", "en": "Jupiter"},
    "Saturn": {"el": "Κρόνος", "en": "Saturn"},
    "Uranus": {"el": "Ουρανός", "en": "Uranus"},
    "Neptune": {"el": "Ποσειδώνας", "en": "Neptune"},
    "Pluto": {"el": "Πλούτωνας", "en": "Pluto"}
}
