# chart_plotter.py - AstroCaterpillar Dual Plotter (Plotly Interactive + Matplotlib PDF)
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
    "Neptune": "♆", "Pluto": "♇"
}

ZODIAC_NAMES_EL = [
    "Κριός (Aries)", "Ταύρος (Taurus)", "Δίδυμοι (Gemini)", "Καρκίνος (Cancer)",
    "Λέων (Leo)", "Παρθένος (Virgo)", "Ζυγός (Libra)", "Σκορπιός (Scorpio)",
    "Τοξότης (Sagittarius)", "Αιγόκερως (Capricorn)", "Υδροχόος (Aquarius)", "Ιχθύες (Pisces)"
]

ZODIAC_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

def extract_planet_info(val):
    if isinstance(val, dict):
        deg = float(val.get("deg", 0.0))
        is_retro = bool(val.get("is_retro", False))
        return deg, is_retro
    return float(val), False

# --- PLOTLY INTERACTIVE CHART (WITH HOUSES NUMBERS, RETROGRADE & OVERLAP HANDLING) ---
def create_interactive_natal_plotly(positions: dict, houses: dict = None):
    fig = go.Figure()

    # 1. Ζώδια στον εξωτερικό δακτύλιο με Tooltips
    z_angles = [i * 30 + 15 for i in range(12)]
    fig.add_trace(go.Scatterpolar(
        r=[1.15] * 12,
        theta=z_angles,
        mode='text',
        text=ZODIAC_SYMBOLS,
        hoverinfo='text',
        hovertext=[f"<b>Ζώδιο:</b> {name}" for name in ZODIAC_NAMES_EL],
        textfont=dict(size=18, color='#60A5FA'),
        name="Ζώδια"
    ))

    # 2. Πλανήτες με διαχείριση επικαλύψεων (Offset)
    sorted_planets = sorted(positions.items(), key=lambda x: extract_planet_info(x[1])[0])
    
    p_r, p_theta, p_text, p_hover, p_color = [], [], [], [], []
    
    prev_deg = -999
    current_radius = 0.85

    for planet, val in sorted_planets:
        deg, is_retro = extract_planet_info(val)
        symbol = PLANET_SYMBOLS.get(planet, planet[:2])
        status = "Ανάδρομος (R)" if is_retro else "Ορθόδρομος"
        
        if abs(deg - prev_deg) < 5.0 or abs(deg - prev_deg) > 355.0:
            current_radius = 0.72 if current_radius == 0.85 else 0.85
        else:
            current_radius = 0.85
        prev_deg = deg

        display_text = f"<b>{symbol} (R)</b>" if is_retro else symbol
        
        p_r.append(current_radius)
        p_theta.append(deg)
        p_text.append(display_text)
        p_hover.append(f"<b>{planet}</b> ({symbol})<br><b>Μοίρα:</b> {deg:.2f}°<br><b>Κατάσταση:</b> {status}")
        p_color.append('#EF4444' if is_retro else '#F59E0B')

    fig.add_trace(go.Scatterpolar(
        r=p_r,
        theta=p_theta,
        mode='markers+text',
        text=p_text,
        hoverinfo='text',
        hovertext=p_hover,
        textposition="top center",
        marker=dict(size=10, color=p_color),
        textfont=dict(size=13, color='#F3F4F6'),
        name="Πλανήτες"
    ))

    # 3. Αιχμές & Αριθμοί 12 Οίκων (1-12) στο εσωτερικό
    if houses and len(houses) >= 12:
        house_degs = [houses.get(f"House_{i}", (i-1)*30) for i in range(1, 13)]
        
        for i in range(12):
            deg_start = house_degs[i]
            deg_end = house_degs[(i + 1) % 12]
            
            # Γραμμή αιχμής
            fig.add_trace(go.Scatterpolar(
                r=[0, 1.05],
                theta=[deg_start, deg_start],
                mode='lines',
                line=dict(color='#374151', width=1, dash='dash'),
                hoverinfo='none',
                showlegend=False
            ))
            
            # Υπολογισμός μέσης γωνίας για τοποθέτηση του αριθμού του Οίκου στο κέντρο (r = 0.38)
            diff = (deg_end - deg_start) % 360.0
            mid_deg = (deg_start + diff / 2.0) % 360.0
            
            fig.add_trace(go.Scatterpolar(
                r=[0.38],
                theta=[mid_deg],
                mode='text',
                text=[str(i + 1)],
                hoverinfo='text',
                hovertext=[f"<b>{i+1}ος Οίκος</b>"],
                textfont=dict(size=11, color='#9CA3AF', weight='bold'),
                showlegend=False
            ))

    fig.update_layout(
        template="plotly_dark",
        polar=dict(
            angularaxis=dict(direction="counterclockwise", rotation=180, showticklabels=False, ticks=""),
            radialaxis=dict(visible=False, range=[0, 1.25])
        ),
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        height=520
    )
    return fig
# --- MATPLOTLIB STATIC CHART (FOR PDF EXPORT) ---
def plot_natal_chart(ax, positions: dict, houses: dict = None):
    ax.clear()
    if hasattr(ax, 'set_theta_direction'):
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location("W")
    ax.set_facecolor('#0E1117')

    for i in range(12):
        angle = np.deg2rad(i * 30 + 15)
        ax.text(angle, 1.15, ZODIAC_SYMBOLS[i], fontsize=14, color='#60A5FA', ha='center', va='center')

    for planet, val in positions.items():
        deg, is_retro = extract_planet_info(val)
        rad = np.deg2rad(deg)
        symbol = PLANET_SYMBOLS.get(planet, planet[:2])
        display_label = f"{symbol} (R)" if is_retro else symbol
        marker_color = '#EF4444' if is_retro else '#F59E0B'
        
        ax.plot(rad, 0.85, 'o', color=marker_color, markersize=6)
        ax.text(rad, 0.95, display_label, fontsize=11, color='#F3F4F6', fontweight='bold' if is_retro else 'normal', ha='center', va='center')

    if houses and len(houses) >= 12:
        house_degs = [houses.get(f"House_{i}", (i-1)*30) for i in range(1, 13)]
        for i in range(12):
            deg_start = house_degs[i]
            deg_end = house_degs[(i + 1) % 12]
            rad_start = np.deg2rad(deg_start)
            ax.plot([rad_start, rad_start], [0, 1.05], color='#374151', linestyle='--', linewidth=0.8)
            
            diff = (deg_end - deg_start) % 360.0
            mid_deg = (deg_start + diff / 2.0) % 360.0
            mid_rad = np.deg2rad(mid_deg)
            ax.text(mid_rad, 0.4, str(i + 1), fontsize=9, color='#9CA3AF', fontweight='bold', ha='center', va='center')

    ax.set_rticks([])
    ax.set_xticks([])
    ax.grid(False)

def plot_biwheel_chart(ax, pos1: dict, pos2: dict):
    ax.clear()
    if hasattr(ax, 'set_theta_direction'):
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location("W")
    ax.set_facecolor('#0E1117')

    for i in range(12):
        angle = np.deg2rad(i * 30 + 15)
        ax.text(angle, 1.25, ZODIAC_SYMBOLS[i], fontsize=13, color='#60A5FA', ha='center', va='center')

    for planet, val in pos1.items():
        deg, is_retro = extract_planet_info(val)
        rad = np.deg2rad(deg)
        symbol = PLANET_SYMBOLS.get(planet, planet[:2])
        label = f"{symbol}(R)" if is_retro else symbol
        ax.plot(rad, 0.6, 'o', color='#10B981', markersize=5)
        ax.text(rad, 0.7, label, fontsize=9, color='#10B981', ha='center', va='center')

    for planet, val in pos2.items():
        deg, is_retro = extract_planet_info(val)
        rad = np.deg2rad(deg)
        symbol = PLANET_SYMBOLS.get(planet, planet[:2])
        label = f"{symbol}(R)" if is_retro else symbol
        ax.plot(rad, 0.95, 'o', color='#EC4899', markersize=5)
        ax.text(rad, 1.05, label, fontsize=9, color='#EC4899', ha='center', va='center')

    ax.set_rticks([])
    ax.set_xticks([])
    ax.grid(False)
