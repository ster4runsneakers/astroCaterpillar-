# chart_plotter.py
import numpy as np
import matplotlib.pyplot as plt

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
    "Neptune": "♆", "Pluto": "♇"
}

ZODIAC_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

def plot_natal_chart(ax, positions: dict, houses: dict = None):
    """Σχεδιάζει έναν γενέθλιο αστρολογικό χάρτη σε πολικές συντεταγμένες."""
    ax.clear()
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("W")
    ax.set_facecolor('#0E1117')

    # Σχεδιασμός 12 Ζωδίων στον εξωτερικό κύκλο
    for i in range(12):
        angle = np.deg2rad(i * 30 + 15)
        ax.text(angle, 1.1, ZODIAC_SYMBOLS[i], fontsize=14, color='#60A5FA', ha='center', va='center')

    # Σχεδιασμός Πλανητών
    for planet, deg in positions.items():
        rad = np.deg2rad(deg)
        symbol = PLANET_SYMBOLS.get(planet, planet[:2])
        ax.plot(rad, 0.8, 'o', color='#F59E0B', markersize=6)
        ax.text(rad, 0.9, symbol, fontsize=12, color='#F3F4F6', ha='center', va='center')

    # Σχεδιασμός Αιχμών Οίκων
    if houses:
        for house_name, deg in houses.items():
            rad = np.deg2rad(deg)
            ax.plot([rad, rad], [0, 1.0], color='#374151', linestyle='--', linewidth=0.8)

    ax.set_rticks([])
    ax.set_xticks([])
    ax.grid(False)

def plot_biwheel_chart(ax, pos1: dict, pos2: dict):
    """Σχεδιάζει έναν διπλό χάρτη (Bi-wheel) για Συναστρία."""
    ax.clear()
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
      
