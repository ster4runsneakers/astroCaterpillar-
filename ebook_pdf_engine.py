# ebook_pdf_engine.py - AstroCaterpillar Full Ebook PDF Engine
import io
import re
from datetime import datetime
from weasyprint import HTML

from ai_engine import analyze_natal_chart_ai, analyze_synastry_ai
from ephemeris_engine import calculate_houses, extract_deg, retro_planets
from elements_engine import calculate_elements_and_modalities
from natal_aspects_engine import calculate_natal_aspects
from synastry_engine import calculate_synastry_aspects
from chinese_astrology import get_chinese_zodiac
from interpretations_el import get_sign_from_degrees
from cities_el import GREEK_AND_WORLD_CITIES, ZODIAC_SIGNS, PLANET_TRANSLATIONS

def create_full_astrology_ebook(profile_name: str, profile_data: dict, lang: str = "el") -> bytes:
    """Υπολογίζει αυτόματα τα αστρολογικά στοιχεία, παράγει την AI ανάλυση και συνθέτει ένα Ebook PDF."""
    
    raw_natal_pos = profile_data.get("positions", {})
    natal_pos = {p: extract_deg(v) for p, v in raw_natal_pos.items()}
    b_date = profile_data.get("date")
    b_time = profile_data.get("time")
    city_name = profile_data.get("city", "Athens")

    lat = GREEK_AND_WORLD_CITIES.get(city_name, {}).get("lat", 37.9838)
    lon = GREEK_AND_WORLD_CITIES.get(city_name, {}).get("lon", 23.7275)
    tz_name = GREEK_AND_WORLD_CITIES.get(city_name, {}).get("tz", "Europe/Athens")

    hour_decimal = b_time.hour + (b_time.minute / 60.0)
    try:
        houses = calculate_houses(
            b_date.year, b_date.month, b_date.day, hour_decimal, lat, lon, tz_name=tz_name
        )
    except TypeError:
        houses = calculate_houses(b_date.year, b_date.month, b_date.day, hour_decimal, lat, lon)

    positions_signs = {planet: get_sign_from_degrees(deg)[0] for planet, deg in natal_pos.items()}
    elements_pct, modalities_pct = calculate_elements_and_modalities(positions_signs)
    aspects = calculate_natal_aspects(natal_pos)
    cz_data = get_chinese_zodiac(b_date.year, b_date.month, b_date.day)
    retro_en = retro_planets(raw_natal_pos, b_date.year, b_date.month, b_date.day, hour_decimal, tz_name)
    retro_el = [PLANET_TRANSLATIONS.get(p, {}).get("el" if lang == "el" else "en", p) for p in retro_en]
    retro_text = ("Αναδρομικοί πλανήτες: " + ", ".join(retro_el)) if (lang == "el" and retro_el) else (
        "Retrograde planets: " + ", ".join(retro_el) if retro_el else
        ("Κανένας πλανήτης δεν είναι αναδρομικός." if lang == "el" else "No planets are retrograde."))

    ai_report_markdown = analyze_natal_chart_ai(
        profile_name,
        str(natal_pos),
        str(houses),
        str(cz_data),
        f"Elements: {elements_pct}, Modalities: {modalities_pct}. {retro_text}",
        str(aspects),
        lang=lang
    )

    if str(ai_report_markdown).startswith("⚠️"):
        try:
            from local_report import build_local_natal
            _h = {}
            try:
                _h = houses
            except Exception:
                pass
            ai_report_markdown = build_local_natal(profile_name, natal_pos, _h) or ai_report_markdown
        except Exception:
            pass

    formatted_ai = ai_report_markdown
    formatted_ai = re.sub(r'###\s*(.*)', r'<h3>\1</h3>', formatted_ai)
    formatted_ai = re.sub(r'##\s*(.*)', r'<h2>\1</h2>', formatted_ai)
    formatted_ai = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_ai)
    formatted_ai = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted_ai)
    formatted_ai = formatted_ai.replace('\n', '<br/>')

    if lang == "el":
        t_title = "AstroCaterpillar Executive Ebook"
        t_profile = "Προφίλ"
        t_datetime = "Ημερομηνία & Ώρα"
        t_city = "Πόλη"
        t_sec1 = "1. Πλανητικές Θέσεις & Μοίρες"
        t_th_planet = "Πλανήτης"
        t_th_sign = "Ζώδιο & Μοίρα"
        t_th_deg = "Συνολική Μοίρα"
        t_sec2 = "2. Πλήρης Αστρολογική & Ψυχογραφική Ανάλυση"
        t_footer = "AstroCaterpillar AI Book — Όλα τα δικαιώματα διατηρούνται"
    else:
        t_title = "AstroCaterpillar Executive Ebook"
        t_profile = "Profile"
        t_datetime = "Date & Time"
        t_city = "City"
        t_sec1 = "1. Planetary Positions & Degrees"
        t_th_planet = "Planet"
        t_th_sign = "Sign & Degree"
        t_th_deg = "Total Absolute Degree"
        t_sec2 = "2. Complete Astrological & Psychological Analysis"
        t_footer = "AstroCaterpillar AI Book — All rights reserved"

    rows_html = ""
    for planet, deg in natal_pos.items():
        sign_en, deg_in = get_sign_from_degrees(deg)
        raw_deg = deg.get("deg", deg) if isinstance(deg, dict) else deg
        sign_display = ZODIAC_SIGNS.get(sign_en, {}).get(lang, sign_en)
        planet_display = PLANET_TRANSLATIONS.get(planet, {}).get(lang, planet)
        r_mark = " ℞" if planet in retro_en else ""
        rows_html += f"""
        <tr>
            <td><strong>{planet_display}{r_mark}</strong></td>
            <td>{deg_in:.1f}° {sign_display}</td>
            <td>{float(raw_deg):.2f}°</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <title>{t_title}</title>
        <style>
            *, *::before, *::after {{ box-sizing: border-box; }}
            @page {{ size: A4; margin: 20mm 15mm; background-color: #0f172a; }}
            body {{ margin: 0; padding: 0; font-family: 'Helvetica Neue', Arial, sans-serif; color: #f1f5f9; line-height: 1.6; font-size: 10.5pt; }}
            .cover-header {{ border-bottom: 3px solid #6366f1; padding-bottom: 15px; margin-bottom: 25px; }}
            h1 {{ font-size: 24pt; color: #818cf8; margin: 0 0 10px 0; letter-spacing: -0.5px; }}
            .meta-info {{ font-size: 9.5pt; color: #94a3b8; background-color: #1e293b; padding: 10px 14px; border-radius: 6px; }}
            h2 {{ font-size: 14pt; color: #a5b4fc; border-left: 5px solid #6366f1; padding-left: 10px; margin-top: 25px; margin-bottom: 12px; page-break-after: avoid; }}
            h3 {{ font-size: 11.5pt; color: #c7d2fe; margin-top: 15px; margin-bottom: 6px; page-break-after: avoid; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; background-color: #1e293b; border-radius: 6px; overflow: hidden; }}
            th {{ background-color: #312e81; color: #e0e7ff; text-align: left; padding: 8px 12px; font-size: 9.5pt; }}
            td {{ padding: 7px 12px; border-bottom: 1px solid #334155; font-size: 9.5pt; }}
            .analysis-text {{ background-color: #1e293b; padding: 18px 20px; border-radius: 8px; border: 1px solid #334155; }}
            .footer {{ text-align: center; font-size: 8pt; color: #64748b; margin-top: 30px; border-top: 1px solid #334155; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="cover-header">
            <h1>{t_title}</h1>
            <div class="meta-info">
                <strong>{t_profile}:</strong> {profile_name} &nbsp;|&nbsp; 
                <strong>{t_datetime}:</strong> {b_date.strftime('%d/%m/%Y')} {b_time.strftime('%H:%M')} &nbsp;|&nbsp; 
                <strong>{t_city}:</strong> {city_name}
            </div>
        </div>

        <h2>{t_sec1}</h2>
        <table>
            <thead>
                <tr>
                    <th>{t_th_planet}</th>
                    <th>{t_th_sign}</th>
                    <th>{t_th_deg}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        <p style="color:#a5b4fc;font-size:10pt;margin-top:-8px;"><strong>℞</strong> {retro_text}</p>

        <h2>{t_sec2}</h2>
        <div class="analysis-text">
            {formatted_ai}
        </div>

        <div class="footer">
            {t_footer}
        </div>
    </body>
    </html>
    """

    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    return pdf_buffer.getvalue()


def create_synastry_ebook(person1_name: str, person2_name: str, prof1_data: dict, prof2_data: dict, lang: str = "el") -> bytes:
    """Παράγει ένα πλήρες Ebook PDF για τη Συναστρία 2 ατόμων."""
    pos1 = prof1_data.get("positions", {})
    pos2 = prof2_data.get("positions", {})
    
    syn_aspects = calculate_synastry_aspects(pos1, pos2)
    
    ai_report_markdown = analyze_synastry_ai(
        person1_name, 
        person2_name, 
        str(syn_aspects), 
        lang=lang
    )

    formatted_ai = ai_report_markdown
    formatted_ai = re.sub(r'###\s*(.*)', r'<h3>\1</h3>', formatted_ai)
    formatted_ai = re.sub(r'##\s*(.*)', r'<h2>\1</h2>', formatted_ai)
    formatted_ai = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_ai)
    formatted_ai = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted_ai)
    formatted_ai = formatted_ai.replace('\n', '<br/>')

    if lang == "el":
        t_title = "AstroCaterpillar Synastry Ebook"
        t_profiles = f"Συναστρία: {person1_name} & {person2_name}"
        t_sec1 = "1. Κύριες Όψεις Συναστρίας"
        t_sec2 = "2. Ψυχογραφική Ανάλυση Σχέσης"
        t_th_p1 = person1_name
        t_th_p2 = person2_name
        t_th_aspect = "Όψη"
        t_th_orb = "Απόκλιση (Orb)"
        t_footer = "AstroCaterpillar AI Synastry Book — Όλα τα δικαιώματα διατηρούνται"
    else:
        t_title = "AstroCaterpillar Synastry Ebook"
        t_profiles = f"Synastry: {person1_name} & {person2_name}"
        t_sec1 = "1. Core Synastry Aspects"
        t_sec2 = "2. Psychological Relationship Analysis"
        t_th_p1 = person1_name
        t_th_p2 = person2_name
        t_th_aspect = "Aspect"
        t_th_orb = "Orb"
        t_footer = "AstroCaterpillar AI Synastry Book — All rights reserved"

    rows_html = ""
    for asp in syn_aspects[:15]:
        p1_clean = asp['p1'].replace("Person1_", "")
        p2_clean = asp['p2'].replace("Person2_", "")
        p1_display = PLANET_TRANSLATIONS.get(p1_clean, {}).get(lang, p1_clean)
        p2_display = PLANET_TRANSLATIONS.get(p2_clean, {}).get(lang, p2_clean)
        
        rows_html += f"""
        <tr>
            <td><strong>{p1_display}</strong></td>
            <td>{asp['aspect']}</td>
            <td><strong>{p2_display}</strong></td>
            <td>{asp['orb']}°</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <title>{t_title}</title>
        <style>
            *, *::before, *::after {{ box-sizing: border-box; }}
            @page {{ size: A4; margin: 20mm 15mm; background-color: #0f172a; }}
            body {{ margin: 0; padding: 0; font-family: 'Helvetica Neue', Arial, sans-serif; color: #f1f5f9; line-height: 1.6; font-size: 10.5pt; }}
            .cover-header {{ border-bottom: 3px solid #ec4899; padding-bottom: 15px; margin-bottom: 25px; }}
            h1 {{ font-size: 24pt; color: #f472b6; margin: 0 0 10px 0; letter-spacing: -0.5px; }}
            .meta-info {{ font-size: 11pt; color: #cbd5e1; background-color: #1e293b; padding: 10px 14px; border-radius: 6px; }}
            h2 {{ font-size: 14pt; color: #fbcfe8; border-left: 5px solid #ec4899; padding-left: 10px; margin-top: 25px; margin-bottom: 12px; page-break-after: avoid; }}
            h3 {{ font-size: 11.5pt; color: #fdf2f8; margin-top: 15px; margin-bottom: 6px; page-break-after: avoid; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; background-color: #1e293b; border-radius: 6px; overflow: hidden; }}
            th {{ background-color: #831843; color: #fce7f3; text-align: left; padding: 8px 12px; font-size: 9.5pt; }}
            td {{ padding: 7px 12px; border-bottom: 1px solid #334155; font-size: 9.5pt; }}
            .analysis-text {{ background-color: #1e293b; padding: 18px 20px; border-radius: 8px; border: 1px solid #334155; }}
            .footer {{ text-align: center; font-size: 8pt; color: #64748b; margin-top: 30px; border-top: 1px solid #334155; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="cover-header">
            <h1>{t_title}</h1>
            <div class="meta-info">
                <strong>{t_profiles}</strong>
            </div>
        </div>

        <h2>{t_sec1}</h2>
        <table>
            <thead>
                <tr>
                    <th>{t_th_p1}</th>
                    <th>{t_th_aspect}</th>
                    <th>{t_th_p2}</th>
                    <th>{t_th_orb}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        <h2>{t_sec2}</h2>
        <div class="analysis-text">
            {formatted_ai}
        </div>

        <div class="footer">
            {t_footer}
        </div>
    </body>
    </html>
    """

    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    return pdf_buffer.getvalue()
