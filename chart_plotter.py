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

# --- PLOTLY INTERACTIVE CHART (FOR BROWSER & MOBILE HOVER/TOUCH) ---
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

    # 2. Πλανήτες με Tooltips
    p_r, p_theta, p_text, p_hover, p_color = [], [], [], [], []
    for planet, val in positions.items():
        deg, is_retro = extract_planet_info(val)
        symbol = PLANET_SYMBOLS.get(planet, planet[:2])
        status = "Ανάδρομος (R)" if is_retro else "Ορθόδρομος"
        
        p_r.append(0.85)
        p_theta.append(deg)
        p_text.append(f"{symbol} (R)" if is_retro else symbol)
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
        textfont=dict(size=14, color='#F3F4F6'),
        name="Πλανήτες"
    ))

    # 3. Αιχμές Οίκων
    if houses and len(houses) >= 12:
        for i in range(1, 13):
            h_deg = houses.get(f"House_{i}", (i-1)*30)
            fig.add_trace(go.Scatterpolar(
                r=[0, 1.05],
                theta=[h_deg, h_deg],
                mode='lines',
                line=dict(color='#374151', width=1, dash='dash'),
                hoverinfo='none',
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
        height=500
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
