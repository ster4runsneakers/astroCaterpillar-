# app.py - AstroCaterpillar Micro-App (Monthly Transits Engine)
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
from synastry_engine import calculate_synastry_aspects, calculate_monthly_transits
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

def export_db_as_json():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT name, date_str, time_str, city, positions_json FROM profiles')
    rows = c.fetchall()
    conn.close()
    
    data = []
    for r in rows:
        data.append({
            "name": r[0],
            "date": r[1],
            "time": r[2],
            "city": r[3],
            "positions": json.loads(r[4])
        })
    return json.dumps(data, indent=2, ensure_ascii=False)

# --- SESSION STATE INITIALIZATION ---
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "guest_profiles" not in st.session_state:
    st.session_state.guest_profiles = {}

# --- LANGUAGE SELECTOR ---
st.sidebar.title("🐛 AstroCaterpillar")
lang_choice = st.sidebar.selectbox("🌐 Γλώσσα / Language", ["Ελληνικά", "English"])
lang = "el" if lang_choice == "Ελληνικά" else "en"

# --- PROFILE SOURCE CONTROLLER ---
if st.session_state.is_admin:
    saved_profiles = load_profiles_from_db()
    st.sidebar.success("🔑 Admin Mode Active" if lang == "el" else "🔑 Admin Mode Active")
else:
    saved_profiles = st.session_state.guest_profiles

# --- SIDEBAR & NAVIGATION ---
t_profiles_header = "👤 Διαχείριση Προφίλ" if lang == "el" else "👤 Profile Management"
st.sidebar.subheader(t_profiles_header)

profile_names = list(saved_profiles.keys())
new_prof_label = "-- Νέο Προφίλ --" if lang == "el" else "-- New Profile --"
selected_profile = st.sidebar.selectbox(
    "Επιλογή Προφίλ:" if lang == "el" else "Select Profile:",
    [new_prof_label] + profile_names
)

if selected_profile == new_prof_label:
    exp_title = "➕ Προσθήκη Προφίλ" if lang == "el" else "➕ Add Profile"
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
        
        btn_save = "💾 Υπολογισμός Χάρτη" if lang == "el" else "💾 Calculate Chart"
        if st.button(btn_save):
            if new_name.strip():
                hour_decimal = new_time.hour + (new_time.minute / 60.0)
                pos = calculate_natal_positions(new_date.year, new_date.month, new_date.day, hour_decimal)
                
                if st.session_state.is_admin:
                    save_profile_to_db(new_name.strip(), new_date, new_time, selected_city_key, pos)
                else:
                    st.session_state.guest_profiles[new_name.strip()] = {
                        "date": new_date, "time": new_time, "city": selected_city_key, "positions": pos
                    }
                st.success("OK!")
                st.rerun()
            else:
                st.error("Παρακαλώ εισάγετε όνομα." if lang == "el" else "Please enter a name.")
else:
    st.sidebar.info(f"**{selected_profile}**")
    btn_del = "🗑️ Αφαίρεση Προφίλ" if lang == "el" else "🗑️ Remove Profile"
    if st.sidebar.button(btn_del):
        if st.session_state.is_admin:
            delete_profile_from_db(selected_profile)
        else:
            del st.session_state.guest_profiles[selected_profile]
        st.rerun()

st.sidebar.markdown("---")

menu_options = [
    "1. Γενέθλιος Χάρτης" if lang == "el" else "1. Natal Chart",
    "2. Μηνιαίες Διελεύσεις" if lang == "el" else "2. Monthly Transits",
    "3. Συναστρία" if lang == "el" else "3. Synastry",
    "4. Εξαγωγή PDF" if lang == "el" else "4. PDF Export",
    "5. Admin Panel"
]
menu_choice = st.sidebar.radio("Πλοήγηση:" if lang == "el" else "Navigation:", menu_options)

# --- MAIN CONTROLLER ---
if selected_profile == new_prof_label and not menu_choice.startswith("5."):
    msg = "👈 Παρακαλώ εισάγετε τα στοιχεία σας στη sidebar για να δημιουργηθεί ο χάρτης σας." if lang == "el" else "👈 Please enter your details in the sidebar to generate your chart."
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

# --- TAB 2: MONTHLY TRANSITS ---
elif menu_choice.startswith("2."):
    st.header(f"📅 Μηνιαίες Διελεύσεις: {selected_profile}" if lang == "el" else f"📅 Monthly Transits: {selected_profile}")
    
    col_t1, col_t2 = st.columns(2)
    
    months_el = ["Ιανουάριος", "Φεβρουάριος", "Μάρτιος", "Απρίλιος", "Μάιος", "Ιούνιος", "Ιούλιος", "Αύγουστος", "Σεπτέμβριος", "Οκτώβριος", "Νοέμβριος", "Δεκέμβριος"]
    months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    months_list = months_el if lang == "el" else months_en
    
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    
    with col_t1:
        sel_month_name = st.selectbox("Επιλογή Μήνα:" if lang == "el" else "Select Month:", months_list, index=current_month - 1)
        sel_month_num = months_list.index(sel_month_name) + 1
    with col_t2:
        sel_year = st.number_input("Επιλογή Έτους:" if lang == "el" else "Select Year:", min_value=2024, max_value=2035, value=current_year)
    
    timeframe_label = f"{sel_month_name} {sel_year}"
    
    if st.button("🔮 Στρατηγική Ανάλυση Μήνα" if lang == "el" else "🔮 Analyze Monthly Trends"):
        with st.spinner("Υπολογισμός Μακρο-Κύκλων..." if lang == "el" else "Calculating Macro Cycles..."):
            m_transits = calculate_monthly_transits(prof_data["positions"], sel_year, sel_month_num)
            report = analyze_transits_ai(selected_profile, timeframe_label, str(m_transits), lang=lang)
            st.markdown(report)

# --- TAB 3: SYNASTRY ---
elif menu_choice.startswith("3."):
    st.header("💞 Συναστρία" if lang == "el" else "💞 Synastry")
    
    if len(profile_names) < 2:
        st.warning("Απαιτούνται τουλάχιστον 2 δημιουργημένα προφίλ στη sidebar." if lang == "el" else "At least 2 profiles in the sidebar are required.")
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
    
    if not st.session_state.is_admin:
        admin_pass = st.text_input("Κωδικός Πρόσβασης / Admin Password:", type="password")
        if st.button("Σύνδεση ως Admin"):
            if admin_pass == "admin123":
                st.session_state.is_admin = True
                st.success("Πρόσβαση εγκρίθηκε!")
                st.rerun()
            else:
                st.error("Λανθασμένος κωδικός πρόσβασης.")
    else:
        st.success("Είστε συνδεδεμένος ως Admin!")
        db_profiles = load_profiles_from_db()
        st.write(f"**Μόνιμα Αποθηκευμένα Προφίλ στη Βάση:** {len(db_profiles)}")
        
        st.markdown("---")
        st.subheader("📦 Εξαγωγή & Backup Βάσης Δεδομένων")
        
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            json_data = export_db_as_json()
            st.download_button(
                label="📥 Download Database (JSON)",
                data=json_data,
                file_name=f"astro_profiles_backup_{datetime.date.today()}.json",
                mime="application/json"
            )
            
        with col_dl2:
            try:
                with open(DB_FILE, "rb") as fp:
                    db_bytes = fp.read()
                st.download_button(
                    label="📥 Download Database (.db)",
                    data=db_bytes,
                    file_name="astro_data.db",
                    mime="application/x-sqlite3"
                )
            except Exception as e:
                st.error("Δεν βρέθηκε το αρχείο βάσης δεδομένων.")

        st.markdown("---")
        col_adm1, col_adm2 = st.columns(2)
        with col_adm1:
            if st.button("🧹 Καθαρισμός AI Cache"):
                clear_ai_cache()
                st.success("Η AI Cache καθαρίστηκε!")
        with col_adm2:
            if st.button("🚪 Αποσύνδεση Admin (Logout)"):
                st.session_state.is_admin = False
                st.rerun()
