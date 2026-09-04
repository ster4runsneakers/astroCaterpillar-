# chart_plotter.py - AstroCaterpillar Chart Plotter Engine
import numpy as np
import matplotlib.pyplot as plt

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
    "Neptune": "♆", "Pluto": "♇"
}

ZODIAC_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

def plot_natal_chart(ax, positions: dict, houses: dict = None):
    """Σχεδιάζει έναν γενέθλιο αστρολογικό χάρτη σε πολικές συντεταγμένες με 12 Οίκους."""
    ax.clear()
    if hasattr(ax, 'set_theta_direction'):
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location("W")
    ax.set_facecolor('#0E1117')

    # 1. Σχεδιασμός 12 Ζωδίων στον εξωτερικό κύκλο
    for i in range(12):
        angle = np.deg2rad(i * 30 + 15)
        ax.text(angle, 1.15, ZODIAC_SYMBOLS[i], fontsize=14, color='#60A5FA', ha='center', va='center')

    # 2. Σχεδιασμός Πλανητών
    for planet, deg in positions.items():
        rad = np.deg2rad(deg)
        symbol = PLANET_SYMBOLS.get(planet, planet[:2])
        ax.plot(rad, 0.85, 'o', color='#F59E0B', markersize=6)
        ax.text(rad, 0.95, symbol, fontsize=12, color='#F3F4F6', ha='center', va='center')

    # 3. Σχεδιασμός Αιχμών και Αριθμών Οίκων (1-12)
    if houses and len(houses) >= 12:
        house_degs = [houses.get(f"House_{i}", (i-1)*30) for i in range(1, 13)]
        
        for i in range(12):
            deg_start = house_degs[i]
            deg_end = house_degs[(i + 1) % 12]
            
            # Γραμμή αιχμής
            rad_start = np.deg2rad(deg_start)
            ax.plot([rad_start, rad_start], [0, 1.05], color='#374151', linestyle='--', linewidth=0.8)
            
            # Υπολογισμός μέσου όρου γωνίας για τοποθέτηση του αριθμού του Οίκου
            diff = (deg_end - deg_start) % 360.0
            mid_deg = (deg_start + diff / 2.0) % 360.0
            mid_rad = np.deg2rad(mid_deg)
            
            # Αναγραφή αριθμού Οίκου στον εσωτερικό κύκλο
            ax.text(mid_rad, 0.4, str(i + 1), fontsize=9, color='#9CA3AF', fontweight='bold', ha='center', va='center')

    ax.set_rticks([])
    ax.set_xticks([])
    ax.grid(False)

def plot_biwheel_chart(ax, pos1: dict, pos2: dict):
    """Σχεδιάζει έναν διπλό χάρτη (Bi-wheel) για Συναστρία."""
    ax.clear()
    if hasattr(ax, 'set_theta_direction'):
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location("W")
    ax.set_facecolor('#0E1117')

    # Ζώδια
    for i in range(12):
        angle = np.deg2rad(i * 30 + 15)
        ax.text(angle, 1.25, ZODIAC_SYMBOLS[i], fontsize=13, color='#60A5FA', ha='center', va='center')

    # Πρώτο Άτομο (Εσωτερικός Κύκλος)
    for planet, deg in pos1.items():
        rad = np.deg2rad(deg)
        symbol = PLANET_SYMBOLS.get(planet, planet[:2])
        ax.plot(rad, 0.6, 'o', color='#10B981', markersize=5)
        ax.text(rad, 0.7, symbol, fontsize=10, color='#10B981', ha='center', va='center')

    # Δεύτερο Άτομο (Εξωτερικός Κύκλος)
    for planet, deg in pos2.items():
        rad = np.deg2rad(deg)
        symbol = PLANET_SYMBOLS.get(planet, planet[:2])
        ax.plot(rad, 0.95, 'o', color='#EC4899', markersize=5)
        ax.text(rad, 1.05, symbol, fontsize=10, color='#EC4899', ha='center', va='center')

    ax.set_rticks([])
    ax.set_xticks([])
    ax.grid(False)
