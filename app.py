# app.py - AstroCaterpillar Micro-App
import datetime
import json
import sqlite3
import streamlit as st
import matplotlib.pyplot as plt

# --- INTERNAL IMPORTS ---
from cities_el import GREEK_AND_WORLD_CITIES, ZODIAC_SIGNS, PLANET_TRANSLATIONS
from ephemeris_engine import calculate_natal_positions, calculate_houses
from interpretations_el import get_sign_from_degrees
from elements_engine import calculate_elements_and_modalities
from natal_aspects_engine import calculate_natal_aspects
from synastry_engine import calculate_synastry_aspects
from chinese_astrology import get_chinese_zodiac
from chart_plotter import plot_natal_chart, plot_biwheel_chart

from ai_engine import (
    analyze_natal_chart_ai,
    analyze_synastry_ai,
    analyze_transits_ai,
    ask_caterpillar_chat,
    clear_ai_cache
)
from pdf_engine import create_astrology_pdf
from ebook_pdf_engine import create_full_astrology_ebook, create_synastry_ebook

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AstroCaterpillar AI",
    page_icon="🐛",
    layout="wide"
)

# --- DATABASE SETUP ---
DB_FILE = "astro_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            name TEXT PRIMARY KEY,
            date_str TEXT,
            time_str TEXT,
            city TEXT,
            positions_json TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def load_profiles_from_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT name, date_str, time_str, city, positions_json FROM profiles')
    rows = c.fetchall()
    conn.close()
    
    profiles = {}
    for r in rows:
        name, d_str, t_str, city, pos_json = r
        try:
            d = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
            t = datetime.datetime.strptime(t_str, "%H:%M").time()
            pos = json.loads(pos_json)
            profiles[name] = {"date": d, "time": t, "city": city, "positions": pos}
        except Exception:
            continue
    return profiles

def save_profile_to_db(name, d, t, city, positions):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    pos_json = json.dumps(positions)
    c.execute(
        'INSERT OR REPLACE INTO profiles (name, date_str, time_str, city, positions_json) VALUES (?, ?, ?, ?, ?)',
        (name, d.strftime("%Y-%m-%d"), t.strftime("%H:%M"), city, pos_json)
    )
    conn.commit()
    conn.close()

def delete_profile_from_db(name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM profiles WHERE name = ?', (name,))
    conn.commit()
    conn.close()

# --- LANGUAGE SELECTOR ---
st.sidebar.title("🐛 AstroCaterpillar")
lang_choice = st.sidebar.selectbox("🌐 Γλώσσα / Language", ["Ελληνικά", "English"])
lang = "el" if lang_choice == "Ελληνικά" else "en"

# --- SIDEBAR & NAVIGATION ---
saved_profiles = load_profiles_from_db()

t_profiles_header = "👤 Διαχείριση Προφίλ" if lang == "el" else "👤 Profile Management"
st.sidebar.subheader(t_profiles_header)

profile_names = list(saved_profiles.keys())
new_prof_label = "-- Νέο Προφίλ --" if lang == "el" else "-- New Profile --"
selected_profile = st.sidebar.selectbox(
    "Επιλογή Προφίλ:" if lang == "el" else "Select Profile:",
    [new_prof_label] + profile_names
)

if selected_profile == new_prof_label:
    exp_title = "➕ Προσθήκη Νέου Προφίλ" if lang == "el" else "➕ Add New Profile"
    with st.sidebar.expander(exp_title, expanded=True):
        new_name = st.text_input("Όνομα / Αρχικά:" if lang == "el" else "Name / Initials:")
        new_date = st.date_input(
            "Ημερομηνία Γέννησης:" if lang == "el" else "Birth Date:",
            value=datetime.date(1990, 1, 1),
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today()
        )
        new_time = st.time_input("Ώρα Γέννησης:" if lang == "el" else "Birth Time:", datetime.time(12, 0))
        
        city_keys = list(GREEK_AND_WORLD_CITIES.keys())
        city_options = {k: GREEK_AND_WORLD_CITIES[k][lang] for k in city_keys}
        selected_city_key = st.selectbox(
            "Πόλη Γέννησης:" if lang == "el" else "Birth City:",
            options=city_keys,
            format_func=lambda x: city_options[x],
            index=city_keys.index("Athens") if "Athens" in city_keys else 0
        )
        
        btn_save = "💾 Αποθήκευση Προφίλ" if lang == "el" else "💾 Save Profile"
        if st.button(btn_save):
            if new_name.strip():
                hour_decimal = new_time.hour + (new_time.minute / 60.0)
                pos = calculate_natal_positions(new_date.year, new_date.month, new_date.day, hour_decimal)
                save_profile_to_db(new_name.strip(), new_date, new_time, selected_city_key, pos)
                st.success("OK!")
                st.rerun()
            else:
                st.error("Παρακαλώ εισάγετε όνομα." if lang == "el" else "Please enter a name.")
else:
    st.sidebar.info(f"**{selected_profile}**")
    btn_del = "🗑️ Διαγραφή Προφίλ" if lang == "el" else "🗑️ Delete Profile"
    if st.sidebar.button(btn_del):
        delete_profile_from_db(selected_profile)
        st.rerun()

st.sidebar.markdown("---")

menu_options = [
    "1. Γενέθλιος Χάρτης" if lang == "el" else "1. Natal Chart",
    "2. Διελεύσεις" if lang == "el" else "2. Transits",
    "3. Συναστρία" if lang == "el" else "3. Synastry",
    "4. Εξαγωγή PDF" if lang == "el" else "4. PDF Export",
    "5. Admin Panel"
]
menu_choice = st.sidebar.radio("Πλοήγηση:" if lang == "el" else "Navigation:", menu_options)

# --- MAIN CONTROLLER ---
if selected_profile == new_prof_label and not menu_choice.startswith("5."):
    msg = "👈 Παρακαλώ επιλέξτε ή δημιουργήστε ένα προφίλ από τη sidebar." if lang == "el" else "👈 Please select or create a profile from the sidebar."
    st.warning(msg)
    st.stop()

prof_data = saved_profiles.get(selected_profile, {})

# --- TAB 1: NATAL CHART ---
if menu_choice.startswith("1."):
    st.header(f"🌌 {selected_profile}")
    
    b_date = prof_data["date"]
    b_time = prof_data["time"]
    city_key = prof_data["city"]
    city_name = GREEK_AND_WORLD_CITIES.get(city_key, {}).get(lang, city_key)
    natal_pos = prof_data["positions"]
    
    lat = GREEK_AND_WORLD_CITIES.get(city_key, {}).get("lat", 37.9838)
    lon = GREEK_AND_WORLD_CITIES.get(city_key, {}).get("lon", 23.7275)
    hour_decimal = b_time.hour + (b_time.minute / 60.0)
    
    houses = calculate_houses(b_date.year, b_date.month, b_date.day, hour_decimal, lat, lon)
    positions_signs = {p: get_sign_from_degrees(deg)[0] for p, deg in natal_pos.items()}
    elements_pct, modalities_pct = calculate_elements_and_modalities(positions_signs)
    aspects = calculate_natal_aspects(natal_pos)
    cz_data = get_chinese_zodiac(b_date.year)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🪐 Αστρολογικός Τροχός" if lang == "el" else "🪐 Astrological Wheel")
        fig, ax = plt.subplots(figsize=(6, 6), facecolor='#0E1117', subplot_kw={'projection': 'polar'})
        plot_natal_chart(ax, natal_pos, houses)
        st.pyplot(fig)
        
    with col2:
        st.subheader("📊 Βασικοί Δείκτες" if lang == "el" else "📊 Key Indicators")
        st.write(f"**Ημερομηνία / Date:** {b_date.strftime('%d/%m/%Y')} {b_time.strftime('%H:%M')} ({city_name})")
        st.write(f"**Κινεζικό Ζώδιο / Chinese Zodiac:** {cz_data.get('animal', '')} ({cz_data.get('element', '')})")
        st.json({"Elements": elements_pct, "Modalities": modalities_pct})

    st.markdown("---")
    st.subheader("🤖 AstroCaterpillar AI Analysis")
    
    btn_ai = "🚀 Παραγωγή AI Ανάλυσης" if lang == "el" else "🚀 Generate AI Analysis"
    if st.button(btn_ai):
        with st.spinner("Ο AstroCaterpillar αναλύει τα δεδομένα..." if lang == "el" else "AstroCaterpillar is analyzing data..."):
            report = analyze_natal_chart_ai(
                selected_profile,
                str(natal_pos),
                str(houses),
                str(cz_data),
                f"Elements: {elements_pct}, Modalities: {modalities_pct}",
                str(aspects),
                lang=lang
            )
            st.session_state[f"natal_ai_{selected_profile}_{lang}"] = report

    cache_key = f"natal_ai_{selected_profile}_{lang}"
    if cache_key in st.session_state:
        report_text = st.session_state[cache_key]
        st.markdown(report_text)
        
        st.markdown("---")
        st.subheader("💬 Chat με τον AstroCaterpillar")
        user_q = st.text_input("Κάνε μια ερώτηση πάνω στην ανάλυσή σου:" if lang == "el" else "Ask a question about your chart:")
        if user_q and st.button("Απάντηση" if lang == "el" else "Answer"):
            with st.spinner("Σκέφτεται..." if lang == "el" else "Thinking..."):
                ans = ask_caterpillar_chat(report_text, user_q, lang=lang)
                st.write(ans)

# --- TAB 2: TRANSITS ---
elif menu_choice.startswith("2."):
    st.header(f"📅 Διελεύσεις: {selected_profile}" if lang == "el" else f"📅 Transits: {selected_profile}")
    target_date = st.date_input("Επιλογή Ημερομηνίας Διέλευσης:" if lang == "el" else "Select Transit Date:", datetime.date.today())
    
    if st.button("🔮 Ανάλυση Διελεύσεων" if lang == "el" else "🔮 Analyze Transits"):
        with st.spinner("Υπολογισμός..." if lang == "el" else "Calculating..."):
            transit_pos = calculate_natal_positions(target_date.year, target_date.month, target_date.day, 12.0)
            transit_aspects = calculate_synastry_aspects(prof_data["positions"], transit_pos)
            report = analyze_transits_ai(selected_profile, target_date.strftime("%d/%m/%Y"), str(transit_aspects), lang=lang)
            st.markdown(report)

# --- TAB 3: SYNASTRY ---
elif menu_choice.startswith("3."):
    st.header("💞 Συναστρία" if lang == "el" else "💞 Synastry")
    
    if len(profile_names) < 2:
        st.warning("Απαιτούνται τουλάχιστον 2 προφίλ στη βάση." if lang == "el" else "At least 2 profiles are required.")
    else:
        p1 = st.selectbox("Πρώτο Άτομο:" if lang == "el" else "Person 1:", profile_names, index=0)
        p2 = st.selectbox("Δεύτερο Άτομο:" if lang == "el" else "Person 2:", profile_names, index=1 if len(profile_names) > 1 else 0)
        
        if p1 != p2:
            if st.button("💖 Υπολογισμός Συναστρίας" if lang == "el" else "💖 Calculate Synastry"):
                pos1 = saved_profiles[p1]["positions"]
                pos2 = saved_profiles[p2]["positions"]
                syn_aspects = calculate_synastry_aspects(pos1, pos2)
                
                fig, ax = plt.subplots(figsize=(6, 6), facecolor='#0E1117', subplot_kw={'projection': 'polar'})
                plot_biwheel_chart(ax, pos1, pos2)
                st.pyplot(fig)
                
                with st.spinner("Ανάλυση..." if lang == "el" else "Analyzing..."):
                    report = analyze_synastry_ai(p1, p2, str(syn_aspects), lang=lang)
                    st.markdown(report)

            st.markdown("---")
            if st.button("📚 Εξαγωγή Synastry Ebook (PDF)"):
                with st.spinner("Σύνθεση Ebook Συναστρίας..." if lang == "el" else "Building Synastry Ebook..."):
                    syn_pdf_bytes = create_synastry_ebook(
                        p1, p2, 
                        saved_profiles[p1], 
                        saved_profiles[p2], 
                        lang=lang
                    )
                    st.download_button(
                        "📥 Download Synastry Ebook (PDF)", 
                        syn_pdf_bytes, 
                        file_name=f"Synastry_{p1}_{p2}.pdf", 
                        mime="application/pdf"
                    )

# --- TAB 4: EXPORT PDF ---
elif menu_choice.startswith("4."):
    st.header(f"📥 Εξαγωγή PDF: {selected_profile}" if lang == "el" else f"📥 PDF Export: {selected_profile}")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📄 One-Pager Summary")
        if st.button("📥 Download One-Pager (PDF)"):
            with st.spinner("Δημιουργία..." if lang == "el" else "Generating..."):
                fig, ax = plt.subplots(figsize=(5, 5), facecolor='#121824', subplot_kw={'projection': 'polar'})
                plot_natal_chart(ax, prof_data["positions"])
                
                pdf_bytes = create_astrology_pdf(
                    "AstroCaterpillar Summary",
                    selected_profile,
                    f"Date: {prof_data['date'].strftime('%d/%m/%Y')} | City: {prof_data['city']}",
                    fig_mat=fig,
                    summary_info=f"Positions: {str(prof_data['positions'])}",
                    ai_summary_text=st.session_state.get(f"natal_ai_{selected_profile}_{lang}", "Δεν έχει παραχθεί AI ανάλυση."),
                    lang=lang
                )
                st.download_button("Download PDF", pdf_bytes, file_name=f"{selected_profile}_summary.pdf", mime="application/pdf")
                
    with col_b:
        st.subheader("📚 Executive Ebook")
        if st.button("📥 Download Ebook (PDF)"):
            with st.spinner("Σύνθεση Ebook..." if lang == "el" else "Building Ebook..."):
                ebook_bytes = create_full_astrology_ebook(selected_profile, prof_data, lang=lang)
                st.download_button("Download Ebook PDF", ebook_bytes, file_name=f"{selected_profile}_Ebook.pdf", mime="application/pdf")

# --- TAB 5: ADMIN PANEL ---
elif menu_choice.startswith("5."):
    st.header("⚙️ Admin Panel")
    admin_pass = st.text_input("Κωδικός Πρόσβασης / Admin Password:", type="password")
    
    if admin_pass == "admin123":
        st.success("Πρόσβαση εγκρίθηκε!")
        st.write(f"**Συνολικά Αποθηκευμένα Προφίλ:** {len(saved_profiles)}")
        
        if st.button("🧹 Καθαρισμός AI Cache (Clear Cache)"):
            clear_ai_cache()
            st.success("Η AI Cache καθαρίστηκε επιτυχώς!")
    elif admin_pass:
        st.error("Λανθασμένος κωδικός πρόσβασης.")
