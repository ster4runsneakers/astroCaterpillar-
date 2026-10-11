# app.py - AstroCaterpillar Micro-App (Includes Persistent Multi-turn Chat for Transits & Synastry)
import datetime
import json
import sqlite3
import streamlit as st
import matplotlib.pyplot as plt

try:
    from streamlit_option_menu import option_menu
    HAS_OPTION_MENU = True
except Exception:
    HAS_OPTION_MENU = False

try:
    import streamlit_antd_components as sac
    HAS_SAC = True
except Exception:
    HAS_SAC = False

# --- INTERNAL IMPORTS ---
from cities_el import GREEK_AND_WORLD_CITIES, ZODIAC_SIGNS, PLANET_TRANSLATIONS
from ephemeris_engine import calculate_natal_positions, calculate_houses


@st.cache_data(show_spinner=False, max_entries=256)
def safe_natal_positions(year, month, day, hour_decimal, tz_name="Europe/Athens"):
    try:
        return calculate_natal_positions(year, month, day, hour_decimal, tz_name=tz_name)
    except TypeError:
        return calculate_natal_positions(year, month, day, hour_decimal)


@st.cache_data(show_spinner=False, max_entries=256)
def safe_houses(year, month, day, hour_decimal, lat, lon, tz_name=None):
    try:
        return calculate_houses(year, month, day, hour_decimal, lat, lon, tz_name=tz_name)
    except TypeError:
        return calculate_houses(year, month, day, hour_decimal, lat, lon)


def safe_chinese_zodiac(year, month=6, day=15):
    try:
        return get_chinese_zodiac(year, month, day)
    except TypeError:
        return get_chinese_zodiac(year)
from interpretations_el import get_sign_from_degrees
from elements_engine import calculate_elements_and_modalities
from natal_aspects_engine import calculate_natal_aspects
from synastry_engine import calculate_synastry_aspects, calculate_monthly_transits
from chinese_astrology import get_chinese_zodiac
from chart_plotter import plot_natal_chart, plot_biwheel_chart, create_interactive_natal_plotly, create_interactive_synastry_plotly

from local_transits import (
    compute_transit_windows, monthly_summary_markdown, month_brief,
)
from summary_el import build_short_summary
from local_report import build_local_natal
import persistence
from ephemeris_engine import retro_planets

from ai_engine import (
    analyze_natal_chart_ai,
    analyze_synastry_ai,
    analyze_transits_ai,
    ask_caterpillar_chat,
    clear_ai_cache,
    set_fresh
)
from pdf_engine import create_astrology_pdf
from ebook_pdf_engine import create_full_astrology_ebook, create_synastry_ebook

@st.cache_data(show_spinner=False, max_entries=64)
def cached_natal_plotly(raw_natal_pos, houses, lang):
    return create_interactive_natal_plotly(raw_natal_pos, houses, lang=lang)


@st.cache_data(show_spinner=False, ttl=6 * 3600, max_entries=32)
def cached_transit_windows(natal_items, start_iso, days=180):
    """natal_items: tuple((σημείο, μοίρες), ...) — κρατιέται στη μνήμη, δεν ξαναϋπολογίζεται."""
    return compute_transit_windows(dict(natal_items), datetime.date.fromisoformat(start_iso), days=days)


def quick_buttons(prefix, options):
    """Έτοιμες ερωτήσεις: επιστρέφει το κείμενο της ερώτησης που πατήθηκε (ή None)."""
    picked = None
    cols = st.columns(len(options))
    for i, (label, q) in enumerate(options):
        if cols[i].button(label, key=f"{prefix}_quick_{i}", use_container_width=True):
            picked = q
    return picked


# --- DICTIONARIES FOR BILINGUAL INDICATORS & GUIDES ---
CHINESE_TRANSLATIONS = {
    "Rat": "Ποντικός / Rat", "Ox": "Βόδι / Ox", "Tiger": "Τίγρης / Tiger",
    "Rabbit": "Λαγός / Rabbit", "Dragon": "Δράκος / Dragon", "Snake": "Φίδι / Snake",
    "Horse": "Άλογο / Horse", "Goat": "Πρόβατο / Goat", "Monkey": "Πίθηκος / Monkey",
    "Rooster": "Πετεινός / Rooster", "Dog": "Σκύλος / Dog", "Pig": "Χοίρος / Pig",
    "Wood": "Ξύλο / Wood", "Fire": "Φωτιά / Fire", "Earth": "Γη / Earth",
    "Metal": "Μέταλλο / Metal", "Water": "Νερό / Water"
}

ELEMENT_TRANSLATIONS = {
    "Fire": "Πυρ / Fire",
    "Earth": "Γη / Earth",
    "Air": "Αέρας / Air",
    "Water": "Νερό / Water"
}

MODALITY_TRANSLATIONS = {
    "Cardinal": "Παρορμητικά / Cardinal",
    "Fixed": "Σταθερά / Fixed",
    "Mutable": "Μεταβλητά / Mutable"
}

HOUSES_GUIDE = {
    "1ος Οίκος / 1st House": "Εαυτός, εξωτερική εικόνα, σώμα, προσωπικότητα, η πρώτη εντύπωση.",
    "2ος Οίκος / 2nd House": "Οικονομικά, προσωπικά εισοδήματα, υλικά αγαθά, αυτοεκτίμηση, προσωπικές αξίες.",
    "3ος Οίκος / 3rd House": "Επικοινωνία, σκέψη, αδέλφια, κοντινά ταξίδια, καθημερινές συναλλαγές, μάθηση.",
    "4ος Οίκος / 4th House": "Ρίζες, οικογένεια, σπίτι, παρελθόν, ψυχική βάση, ο ένας γονέας.",
    "5ος Οίκος / 5th House": "Δημιουργικότητα, έρωτας, παιδιά, διασκέδαση, επιχειρηματικό ρίσκο, αυτοέκφραση.",
    "6ος Οίκος / 6th House": "Καθημερινή εργασία, υγεία, ευεξία, ρουτίνα, υποχρεώσεις, προσφορά.",
    "7ος Οίκος / 7th House": "Σχέσεις, γάμος, συνεργασίες, φανεροί εχθροί, κοινωνικές δεσμεύσεις.",
    "8ος Οίκος / 8th House": "Κοινά οικονομικά, κληρονομιές, μετασχηματισμός, ψυχικό βάθος, σεξουαλικότητα, αναγέννηση.",
    "9ος Οίκος / 9th House": "Ανώτερη γνώση, φιλοσοφία, μακρινά ταξίδια, νομικά θέματα, πεποιθήσεις.",
    "10ος Οίκος / 10th House": "Καριέρα, κοινωνική καταξίωση, δημόσια εικόνα, φιλοδοξίες, κύρος.",
    "11ος Οίκος / 11th House": "Φίλοι, συλλογικότητες, ομάδες, στόχοι, ελπίδες, κοινωνικά δίκτυα.",
    "12ος Οίκος / 12th House": "Υποσυνείδητο, κρυφοί εχθροί, απομόνωση, ψυχική θεραπεία, καρμικά χρέη, πνευματικότητα."
}

ZODIAC_GUIDE = {
    "Κριός / Aries": "Πυρ - Παρορμητικό | Πρωτοβουλία, δράση, θάρρος, παρορμητισμός, ηγεσία.",
    "Ταύρος / Taurus": "Γη - Σταθερό | Σταθερότητα, ασφάλεια, υπομονή, υλική απόλαυση, επιμονή.",
    "Δίδυμοι / Gemini": "Αέρας - Μεταβλητό | Προσαρμοστικότητα, περιέργεια, επικοινωνία, ευελιξία, διάνοια.",
    "Καρκίνος / Cancer": "Νερό - Παρορμητικό | Συναισθηματική προστασία, φροντίδα, διαίσθηση, οικογένεια.",
    "Λέων / Leo": "Πυρ - Σταθερό | Αυτοπεποίθηση, γενναιοδωρία, δημιουργικότητα, ηγετικό πνεύμα.",
    "Παρθένος / Virgo": "Γη - Μεταβλητό | Αναλυτική σκέψη, λεπτομέρεια, πρακτικότητα, τελειομανία, προσφορά.",
    "Ζυγός / Libra": "Αέρας - Παρορμητικό | Ισορροπία, αρμονία, δικαιοσύνη, συντροφικότητα, αισθητική.",
    "Σκορπιός / Scorpio": "Νερό - Σταθερό | Βάθος, πάθος, μετασχηματισμός, έλεγχος, διαίσθηση.",
    "Τοξότης / Sagittarius": "Πυρ - Μεταβλητό | Αισιοδοξία, επέκταση, αναζήτηση αλήθειας, ελευθερία, σοφία.",
    "Αιγόκερως / Capricorn": "Γη - Παρορμητικό | Πειθαρχία, φιλοδοξία, δομή, ευθύνη, μακροπρόθεσμος σχεδιασμός.",
    "Υδροχόος / Aquarius": "Αέρας - Σταθερό | Ανεξαρτησία, πρωτοπορία, συλλογικότητα, αυθεντικότητα, οραματισμός.",
    "Ιχθύες / Pisces": "Νερό - Μεταβλητό | Ενσυναίσθηση, φαντασία, πνευματικότητα, συμπόνια, υπέρβαση."
}

RETROGRADE_GUIDE = {
    "Ερμής / Mercury (R)": "Επανεξέταση επικοινωνίας, συμφωνιών, εγγράφων. Εσωστρέφεια στη σκέψη, πιθανές καθυστερήσεις.",
    "Αφροδίτη / Venus (R)": "Αναθεώρηση σχέσεων, συναισθηματικών αναγκών και οικονομικών αξιών. Επιστροφή παρελθόντος.",
    "Άρης / Mars (R)": "Εσωτερικευμένη δράση, ανάσχεση παρορμητισμού, επανεξέταση στόχων και διαχείριση θυμού.",
    "Δίας / Jupiter (R)": "Εσωτερική φιλοσοφική ανάπτυξη, επανεξέταση πεποιθήσεων και προσωπικής ηθικής.",
    "Κρόνος / Saturn (R)": "Αναθεώρηση δομών, ορίων και ευθυνών. Εσωτερική πειθαρχία και καρμική ωρίμανση.",
    "Ουρανός / Uranus (R)": "Εσωτερική επαναστατικότητα, αναθεώρηση προσωπικής ελευθερίας και απρόσμενες συνειδητοποιήσεις.",
    "Ποσειδώνας / Neptune (R)": "Διάλυση αυταπατών, ενίσχυση διαίσθησης, πνευματική αφύπνιση.",
    "Πλούτωνας / Pluto (R)": "Βαθύς ψυχικός μετασχηματισμός, αποδέσμευση από παλιές δομές εξουσίας και μοτίβα ελέγχου."
}

ELEMENTS_GUIDE = {
    "🔥 Πυρ / Fire": "Έμπνευση, πάθος, ζωτικότητα, παρορμητισμός, θάρρος, ενθουσιασμός. Άμεση δράση και ηγεσία.",
    "🌿 Γη / Earth": "Σταθερότητα, πρακτικότητα, υλική ασφάλεια, ρεαλισμός, δομή, επιμονή. Εστίαση στο απτό αποτέλεσμα.",
    "💨 Αέρας / Air": "Διάνοια, επικοινωνία, ιδέες, κοινωνικότητα, στρατηγική σκέψη. Λειτουργία μέσω του νου και της πληροφορίας.",
    "🌊 Νερό / Water": "Συναισθήματα, διαίσθηση, ενσυναίσθηση, ψυχικό βάθος, μνήμη. Αντίληψη μέσω των αισθήσεων."
}

MODALITIES_GUIDE = {
    "⚡ Παρορμητικά / Cardinal": "Η Αρχή & η Πρωτοβουλία. Ανοίγουν νέους δρόμους, ξεκινούν έργα, θέτουν στόχους.",
    "🏛️ Σταθερά / Fixed": "Η Διατήρηση & η Θεμελίωση. Συγκεντρώνουν, σταθεροποιούν και προστατεύουν με αφοσίωση.",
    "🌀 Μεταβλητά / Mutable": "Η Προσαρμογή & η Μετάβαση. Προσαρμόζονται, βελτιώνουν, διορθώνουν και εξελίσσουν."
}

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AstroCaterpillar AI",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Source+Sans+3:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }
.stApp {
  background:
    radial-gradient(900px 480px at 8% -8%, rgba(56,89,140,.45), transparent 55%),
    radial-gradient(700px 420px at 100% 0%, rgba(88,28,135,.18), transparent 50%),
    #070B14;
  color: #E2E8F0;
}
.block-container { padding-top: 1.4rem; padding-bottom: 2.5rem; max-width: 1280px; }
#MainMenu, footer { visibility: hidden; }
header { visibility: visible !important; }
[data-testid="stHeader"] {
  background: rgba(7,11,20,.88) !important;
  backdrop-filter: blur(8px);
}
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
  visibility: visible !important;
  display: flex !important;
  color: #93C5FD !important;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0C1524 0%, #0A101C 100%);
  border-right: 1px solid rgba(148,163,184,.12);
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #F1F5F9; }
.stButton>button {
  background: linear-gradient(180deg, #3B82F6 0%, #2563EB 100%);
  color: #fff; border: 0; border-radius: 12px;
  padding: .55rem 1rem; font-weight: 600; letter-spacing: .01em;
  box-shadow: 0 8px 24px rgba(37,99,235,.25);
}
.stButton>button:hover { filter: brightness(1.08); }
.stDownloadButton>button {
  background: #0F172A; color: #93C5FD;
  border: 1px solid rgba(147,197,253,.35); border-radius: 12px;
}
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-testid="stDateInput"] input {
  background: #0F172A !important; border-radius: 10px !important;
  border: 1px solid rgba(148,163,184,.22) !important; color: #F8FAFC !important;
}
h1, h2, h3 { font-family: 'Cormorant Garamond', serif; color: #F8FAFC; letter-spacing: -.02em; }
.stRadio > label { color: #CBD5E1; }
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
.ac-hero {
  background: linear-gradient(155deg, rgba(30,58,95,.62) 0%, rgba(15,23,42,.28) 100%);
  border: 1px solid rgba(147,197,253,.16);
  border-radius: 24px; padding: 2.3rem 2rem 1.9rem; margin-bottom: 1.15rem;
}
.ac-kicker { color:#93C5FD; letter-spacing:.2em; font-size:.72rem; font-weight:600; text-transform:uppercase; margin:0 0 .45rem 0; }
.ac-title { font-family:'Cormorant Garamond',serif; font-size:clamp(2.2rem,5vw,3.15rem); line-height:1.05; color:#F8FAFC; margin:0 0 .55rem 0; }
.ac-sub { color:#CBD5E1; font-size:1.05rem; line-height:1.6; max-width:46rem; }
.ac-card {
  background: rgba(15,23,42,.78);
  border: 1px solid rgba(148,163,184,.14);
  border-radius: 16px; padding: 1.15rem 1.1rem; height: 100%;
}
.ac-card h3 { font-family:'Cormorant Garamond',serif; color:#E0E7FF; font-size:1.32rem; margin:0 0 .35rem 0; }
.ac-card p { color:#94A3B8; font-size:.92rem; margin:0; line-height:1.5; }
.ac-step { color:#64748B; font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; margin:0 0 .25rem 0; }
.ac-foot { color:#64748B; font-size:.85rem; text-align:center; margin-top:1.5rem; line-height:1.55; }

/* ---- COMPACT UI ---- */
.block-container { padding-top: .6rem !important; padding-bottom: 1.2rem !important; max-width: 1180px !important; }
[data-testid="stVerticalBlock"] { gap: .55rem !important; }
[data-testid="stSidebar"] { min-width: 235px !important; max-width: 260px !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .4rem !important; }
[data-testid="stSidebarUserContent"] { padding-top: .8rem !important; }
h1 { font-size: 1.7rem !important; margin: .2rem 0 .3rem !important; padding: 0 !important; }
h2 { font-size: 1.4rem !important; margin: .2rem 0 .25rem !important; padding: 0 !important; }
h3 { font-size: 1.12rem !important; margin: .15rem 0 .2rem !important; padding: 0 !important; }
h4 { font-size: 1rem !important; margin: .1rem 0 !important; }
p, li, .stMarkdown { font-size: .93rem; line-height: 1.45; }
hr { margin: .6rem 0 !important; }
.stButton>button, .stDownloadButton>button { padding: .35rem .8rem !important; font-size: .9rem !important; border-radius: 10px !important; box-shadow: none !important; }
div[data-testid="stExpander"] { margin: 0 !important; }
div[data-testid="stExpander"] summary { padding: .35rem .6rem !important; font-size: .9rem; }
[data-testid="stDataFrame"] { font-size: .85rem; }
div[data-testid="stAlert"] { padding: .5rem .75rem !important; }
.ac-hero { padding: 1.1rem 1.1rem .9rem !important; border-radius: 16px !important; margin-bottom: .6rem !important; }
.ac-title { font-size: clamp(1.5rem,3.5vw,2.1rem) !important; margin: 0 0 .3rem !important; }
.ac-sub { font-size: .92rem !important; line-height: 1.45 !important; }
.ac-card { padding: .7rem .8rem !important; border-radius: 12px !important; }
.ac-card h3 { font-size: 1.05rem !important; }
.ac-card p { font-size: .85rem !important; }
.ac-foot { margin-top: .6rem !important; font-size: .78rem !important; }
[data-testid="stChatMessage"] { padding: .5rem .7rem !important; }
@media (max-width: 640px) { .block-container { padding-left: .7rem !important; padding-right: .7rem !important; } }

/* ---- TOP NAV (χωρίς sidebar) ---- */
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] { display: none !important; }
.ac-brand { font-size: 1.05rem; margin: 0 0 .1rem 0; color: #E2E8F0; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE SETUP (ADMIN ONLY) ---
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
    sync_backup()

def delete_profile_from_db(name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM profiles WHERE name = ?', (name,))
    conn.commit()
    conn.close()
    sync_backup()

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

def import_db_from_json(json_content):
    data = json.loads(json_content)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    imported_count = 0
    for item in data:
        name = item.get("name")
        d_str = item.get("date")
        t_str = item.get("time")
        city = item.get("city")
        positions = item.get("positions")
        if name and d_str and t_str and city and positions:
            pos_json = json.dumps(positions)
            c.execute(
                'INSERT OR REPLACE INTO profiles (name, date_str, time_str, city, positions_json) VALUES (?, ?, ?, ?, ?)',
                (name, d_str, t_str, city, pos_json)
            )
            imported_count += 1
    conn.commit()
    conn.close()
    if imported_count:
        try:
            sync_backup()
        except Exception:
            pass
    return imported_count

def _backup_token():
    try:
        from ai_engine import _secret
        return _secret("GITHUB_TOKEN")
    except Exception:
        return ""


def sync_backup():
    """Μετά από κάθε αλλαγή προφίλ: στέλνει αντίγραφο στο GitHub (αν υπάρχει GITHUB_TOKEN στα Secrets)."""
    token = _backup_token()
    if not token:
        st.session_state["backup_status"] = "Δεν έχει οριστεί GITHUB_TOKEN — το αντίγραφο ασφαλείας είναι χειροκίνητο."
        return
    ok, msg = persistence.push_gist(token, export_db_as_json())
    st.session_state["backup_status"] = ("✅ " if ok else "⚠️ ") + msg


def count_db_profiles():
    conn = sqlite3.connect(DB_FILE)
    n = conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0]
    conn.close()
    return n


def auto_restore_profiles():
    """Αν η βάση είναι άδεια (π.χ. μετά από restart): επαναφορά από GitHub gist ή από profiles_backup.json."""
    if st.session_state.get("_restore_tried"):
        return
    st.session_state["_restore_tried"] = True
    try:
        if count_db_profiles() > 0:
            return
        token = _backup_token()
        for source, text in (("GitHub backup", persistence.pull_gist(token) if token else None),
                             ("profiles_backup.json", persistence.read_file_backup())):
            if text and persistence.validate_backup(text):
                n = import_db_from_json(text)
                st.session_state["backup_status"] = f"♻️ Επαναφέρθηκαν {n} προφίλ από {source}."
                return
    except Exception:
        pass


def guest_profiles_from_json(text):
    data = json.loads(text)
    n = 0
    for it in data:
        try:
            st.session_state.guest_profiles[it["name"]] = {
                "date": datetime.datetime.strptime(it["date"], "%Y-%m-%d").date(),
                "time": datetime.datetime.strptime(it["time"], "%H:%M").time(),
                "city": it["city"], "positions": it["positions"],
            }
            n += 1
        except Exception:
            continue
    return n


# --- SESSION STATE INITIALIZATION ---
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

auto_restore_profiles()

if "guest_profiles" not in st.session_state:
    st.session_state.guest_profiles = {}

# Chat memory stores per category
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

def collect_and_save_profile(key_prefix="sb"):
    """Φόρμα νέου προφίλ — ίδια στη sidebar και στην αρχική (για κινητά)."""
    new_name = st.text_input("Όνομα / Αρχικά", key=f"{key_prefix}_name")
    new_date = st.date_input(
        "Ημερομηνία Γέννησης",
        value=datetime.date(1990, 1, 1),
        min_value=datetime.date(1900, 1, 1),
        max_value=datetime.date.today(),
        key=f"{key_prefix}_date",
    )
    unknown_time = st.checkbox(
        "Δεν γνωρίζω ώρα γέννησης",
        key=f"{key_prefix}_unk",
    )
    new_time = st.time_input(
        "Ώρα Γέννησης",
        datetime.time(12, 0),
        disabled=unknown_time,
        key=f"{key_prefix}_time",
    )
    city_filter = st.text_input("Αναζήτηση πόλης", key=f"{key_prefix}_cityq")
    city_keys = list(GREEK_AND_WORLD_CITIES.keys())
    if city_filter.strip():
        q = city_filter.strip().lower()
        city_keys = [
            k for k in city_keys
            if q in k.lower()
            or q in GREEK_AND_WORLD_CITIES[k].get("el", "").lower()
            or q in GREEK_AND_WORLD_CITIES[k].get("en", "").lower()
        ] or list(GREEK_AND_WORLD_CITIES.keys())
    city_options = {
        k: f"{GREEK_AND_WORLD_CITIES[k]['el']} / {GREEK_AND_WORLD_CITIES[k]['en']}"
        for k in city_keys
    }
    default_ix = city_keys.index("Athens") if "Athens" in city_keys else 0
    selected_city_key = st.selectbox(
        "Πόλη Γέννησης",
        options=city_keys,
        format_func=lambda x: city_options[x],
        index=default_ix,
        key=f"{key_prefix}_city",
    )
    if st.button("💾 Υπολογισμός Χάρτη", key=f"{key_prefix}_go"):
        if not new_name.strip():
            st.error("Γράψε ένα όνομα ή αρχικά.")
            return False
        if unknown_time:
            new_time = datetime.time(12, 0)
        hour_decimal = new_time.hour + (new_time.minute / 60.0)
        tz_name = GREEK_AND_WORLD_CITIES.get(selected_city_key, {}).get("tz", "Europe/Athens")
        pos = safe_natal_positions(
            new_date.year, new_date.month, new_date.day, hour_decimal, tz_name=tz_name
        )
        if st.session_state.is_admin:
            save_profile_to_db(new_name.strip(), new_date, new_time, selected_city_key, pos)
        else:
            st.session_state.guest_profiles[new_name.strip()] = {
                "date": new_date,
                "time": new_time,
                "city": selected_city_key,
                "positions": pos,
                "unknown_time": unknown_time,
            }
        st.success("Ο χάρτης υπολογίστηκε.")
        st.rerun()
    return True


# --- TOP BAR (γλώσσα + προφίλ) ---
st.markdown('<p class="ac-brand">🐛 <b>AstroCaterpillar</b> AI</p>', unsafe_allow_html=True)
bar1, bar2 = st.columns([1, 2.4])
with bar1:
    lang_choice = st.selectbox("🌐 Γλώσσα / Language", ["Ελληνικά", "English"])
lang = "el" if lang_choice == "Ελληνικά" else "en"

# --- PROFILE SOURCE CONTROLLER ---
if st.session_state.is_admin:
    saved_profiles = load_profiles_from_db()
else:
    saved_profiles = st.session_state.guest_profiles

profile_names = list(saved_profiles.keys())
new_prof_label = "-- Νέο Προφίλ / New Profile --"
with bar2:
    selected_profile = st.selectbox(
        "👤 Προφίλ / Profile" + ("  ·  🔑 Admin" if st.session_state.is_admin else ""),
        [new_prof_label] + profile_names,
    )

if selected_profile == new_prof_label:
    with st.expander("➕ Προσθήκη Προφίλ / Add Profile", expanded=True):
        collect_and_save_profile("sb")
else:
    act1, act2, act3 = st.columns([1, 1, 3])
    with act1:
        if st.button("🗑️ Αφαίρεση / Remove"):
            if st.session_state.is_admin:
                delete_profile_from_db(selected_profile)
            else:
                del st.session_state.guest_profiles[selected_profile]
            st.rerun()
    with act2:
        if saved_profiles and not st.session_state.is_admin:
            export_rows = []
            for nm, pr in saved_profiles.items():
                export_rows.append({
                    "name": nm,
                    "date": pr["date"].strftime("%Y-%m-%d") if hasattr(pr["date"], "strftime") else str(pr["date"]),
                    "time": pr["time"].strftime("%H:%M") if hasattr(pr["time"], "strftime") else str(pr["time"]),
                    "city": pr.get("city"),
                    "positions": pr.get("positions"),
                })
            st.download_button(
                "📥 Backup (JSON)",
                data=json.dumps(export_rows, ensure_ascii=False, indent=2),
                file_name="astro_guest_backup.json",
                mime="application/json",
            )

if selected_profile != new_prof_label and not st.session_state.is_admin:
    with st.expander("📤 Φόρτωση backup προφίλ (JSON)"):
        _gu = st.file_uploader("Αρχείο backup", type=["json"], key="guest_bk_up")
        if _gu is not None and st.button("Φόρτωση", key="guest_bk_go"):
            try:
                n = guest_profiles_from_json(_gu.read().decode("utf-8"))
                st.success(f"Φορτώθηκαν {n} προφίλ.")
                st.rerun()
            except Exception as e:
                st.error(f"Σφάλμα: {e}")

menu_options = [
    "1. Γενέθλιος Χάρτης / Natal Chart",
    "2. Μηνιαίες Διελεύσεις / Monthly Transits",
    "3. Συναστρία / Synastry",
    "4. Εξαγωγή PDF / PDF Export",
    "5. Οδηγός Αστρολογίας / Astrology Guide",
    "6. Admin Panel"
]
menu_labels = ["Χάρτης", "Διελεύσεις", "Συναστρία", "PDF", "Οδηγός", "Admin"]
if HAS_OPTION_MENU:
    _sel = option_menu(
        menu_title=None,
        options=menu_labels,
        icons=["stars", "calendar3", "heart", "file-earmark-pdf", "book", "gear"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"background-color": "rgba(15,23,42,.7)", "padding": "2px", "border-radius": "12px"},
            "icon": {"color": "#93C5FD", "font-size": "14px"},
            "nav-link": {"color": "#E2E8F0", "font-size": "13px", "text-align": "center",
                         "margin": "0 1px", "padding": "6px 8px", "--hover-color": "#1E293B"},
            "nav-link-selected": {"background-color": "#1D4ED8"},
        },
    )
else:
    _sel = st.radio("Πλοήγηση", menu_labels, horizontal=True, label_visibility="collapsed")
menu_choice = menu_options[menu_labels.index(_sel)]

# --- MAIN CONTROLLER ---
if selected_profile == new_prof_label and not (menu_choice.startswith("5.") or menu_choice.startswith("6.")):
    st.markdown("""
    <div class="ac-hero">
      <p class="ac-kicker">Self-custody astrological studio</p>
      <h1 class="ac-title">🐛 AstroCaterpillar</h1>
      <p class="ac-sub">
        Γενέθλιος χάρτης, διελεύσεις και συναστρία — με ακρίβεια επιμεληρίου και αφήγηση AI.
        Τα δεδομένα μένουν στη συσκευή σου. Συμπλήρωσε τη φόρμα «Προσθήκη Προφίλ» από πάνω.
      </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("🌌", "Γενέθλιος χάρτης", "Πλανήτες, οίκοι, όψεις, στοιχεία και κινεζικό ζώδιο σε διαδραστικό τροχό."),
        ("📅", "Διελεύσεις", "Μακρο-κύκλοι του μήνα: ευκαιρίες και εντάσεις σε σχέση με τον γενέθλιο."),
        ("💞", "Συναστρία", "Δύο χάρτες στον ίδιο τροχό και έκθεση συμβατότητας."),
        ("📥", "PDF / Ebook", "One-pager ή πλήρες βιβλίο για προσωπική αρχειοθέτηση."),
    ]
    for col, (icon, title, body) in zip((c1, c2, c3, c4), cards):
        col.markdown(
            f'<div class="ac-card"><p class="ac-step">{icon}</p><h3>{title}</h3><p>{body}</p></div>',
            unsafe_allow_html=True,
        )

    with st.expander("📱 Ξεκίνα εδώ (ιδανικό από κινητό)", expanded=True):
        collect_and_save_profile("mob")
    if HAS_SAC:
        try:
            sac.steps(
                items=[
                    sac.StepsItem(title="Όνομα", description="Αριστερά στη στήλη"),
                    sac.StepsItem(title="Γέννηση", description="Ημερομηνία, ώρα, πόλη"),
                    sac.StepsItem(title="Υπολογισμός", description="Κουμπί χάρτη"),
                ],
                index=0,
                size="sm",
                color="blue",
            )
        except Exception:
            pass
    s1, s2, s3 = st.columns(3)
    steps = [
        ("01", "Όνομα", "Γράψε όνομα ή αρχικά στην sidebar. Δεν αποθηκεύεται σε εξωτερικό server (guest mode)."),
        ("02", "Γέννηση", "Ημερομηνία, ώρα και πόλη. Η ώρα χρειάζεται για σωστό ωροσκόπο."),
        ("03", "Υπολογισμός", "Πάτα «Υπολογισμός Χάρτη». Μετά ανοίγει ο τροχός και η AI ανάλυση."),
    ]
    for col, (num, title, body) in zip((s1, s2, s3), steps):
        col.markdown(
            f'<div class="ac-card"><p class="ac-step">Βήμα {num}</p><h3>{title}</h3><p>{body}</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p class="ac-foot">↑ Συμπλήρωσε τα πεδία στη φόρμα πάνω και πάτα Υπολογισμός Χάρτη<br/>Η εφαρμογή είναι συμβολική / ψυχαγωγική — όχι ιατρική, νομική ή οικονομική συμβουλή.</p>',
        unsafe_allow_html=True,
    )
    st.stop()

prof_data = saved_profiles.get(selected_profile, {})

def extract_deg(val):
    if isinstance(val, dict):
        return float(val.get("deg", 0.0))
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def house_of_degree(deg, houses):
    try:
        cusps = [float(houses.get(f"House_{i}", (i - 1) * 30)) % 360.0 for i in range(1, 13)]
    except Exception:
        return None
    d = float(deg) % 360.0
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        if start <= end:
            if start <= d < end:
                return i + 1
        else:
            if d >= start or d < end:
                return i + 1
    return 1


def format_chart_brief(natal_pos, houses, aspects, lang="el"):
    lines = []
    for planet, deg in natal_pos.items():
        sign, din = get_sign_from_degrees(deg)
        sign_l = ZODIAC_SIGNS.get(sign, {}).get(lang, sign)
        pname = PLANET_TRANSLATIONS.get(planet, {}).get(lang, planet)
        h = house_of_degree(deg, houses) if houses else "-"
        lines.append(f"{pname}: {din:.1f}° {sign_l}, οίκος {h}")
    asp_lines = []
    for a in aspects[:18]:
        p1 = PLANET_TRANSLATIONS.get(a["p1"], {}).get(lang, a["p1"])
        p2 = PLANET_TRANSLATIONS.get(a["p2"], {}).get(lang, a["p2"])
        asp_lines.append(f"{p1} {a['aspect']} {p2} (orb {a['orb']}°)")
    return "\n".join(lines), "\n".join(asp_lines)


def chat_bucket(kind, profile_key):
    key = f"{kind}:{profile_key}"
    if key not in st.session_state.chat_history:
        st.session_state.chat_history[key] = []
    return key

# --- TAB 1: NATAL CHART ---
if menu_choice.startswith("1."):
    st.header(f"🌌 {selected_profile}")
    
    b_date = prof_data["date"]
    b_time = prof_data["time"]
    city_key = prof_data["city"]
    city_name_el = GREEK_AND_WORLD_CITIES.get(city_key, {}).get("el", city_key)
    city_name_en = GREEK_AND_WORLD_CITIES.get(city_key, {}).get("en", city_key)
    raw_natal_pos = prof_data["positions"]
    natal_pos = {p: extract_deg(v) for p, v in raw_natal_pos.items()}
    
    lat = GREEK_AND_WORLD_CITIES.get(city_key, {}).get("lat", 37.9838)
    lon = GREEK_AND_WORLD_CITIES.get(city_key, {}).get("lon", 23.7275)
    tz_name = GREEK_AND_WORLD_CITIES.get(city_key, {}).get("tz", "Europe/Athens")

    local_hour_decimal = b_time.hour + (b_time.minute / 60.0)
    houses = safe_houses(
        b_date.year, b_date.month, b_date.day, local_hour_decimal, lat, lon, tz_name=tz_name
    )
    positions_signs = {p: get_sign_from_degrees(deg)[0] for p, deg in natal_pos.items()}
    elements_pct, modalities_pct = calculate_elements_and_modalities(positions_signs)
    aspects = calculate_natal_aspects(natal_pos)
    cz_data = safe_chinese_zodiac(b_date.year, b_date.month, b_date.day)

    cz_animal_raw = cz_data.get('animal', '')
    cz_element_raw = cz_data.get('element', '')
    cz_animal_bi = CHINESE_TRANSLATIONS.get(cz_animal_raw, cz_animal_raw)
    cz_element_bi = CHINESE_TRANSLATIONS.get(cz_element_raw, cz_element_raw)

    try:
        _retro_en = retro_planets(
            raw_natal_pos, b_date.year, b_date.month, b_date.day,
            b_time.hour + b_time.minute / 60.0, tz_name=tz_name,
        )
    except Exception:
        _retro_en = []
    _brief = build_short_summary(selected_profile, natal_pos, houses, _retro_en)
    if _brief:
        st.markdown("### ✨ Σύνοψη")
        st.markdown(_brief)
        st.markdown("---")

    col1, col2 = st.columns([1.1, 0.9])
    
    with col1:
        st.subheader("🪐 Διαδραστικός Χάρτης (Hover/Touch) / Interactive Chart")
        plotly_fig = cached_natal_plotly(raw_natal_pos, houses, lang)
        st.plotly_chart(plotly_fig, use_container_width=True)
        # Αναδρομικότητα: αν το αποθηκευμένο προφίλ δεν έχει σημαία (παλιά δεδομένα), ξαναϋπολογίζεται
        retro_src = raw_natal_pos
        if not any(isinstance(v, dict) and "is_retro" in v for v in raw_natal_pos.values()):
            try:
                retro_src = safe_natal_positions(
                    b_date.year, b_date.month, b_date.day,
                    b_time.hour + b_time.minute / 60.0, tz_name=tz_name
                )
            except Exception:
                retro_src = raw_natal_pos
        table_rows = []
        retro_names = []
        for planet, deg in natal_pos.items():
            sign, din = get_sign_from_degrees(deg)
            sign_el = ZODIAC_SIGNS.get(sign, {}).get("el", sign)
            raw = retro_src.get(planet)
            is_r = bool(isinstance(raw, dict) and raw.get("is_retro"))
            pname = PLANET_TRANSLATIONS.get(planet, {}).get("el", planet)
            if is_r:
                retro_names.append(pname)
            table_rows.append({
                "Πλανήτης": pname,
                "Ζώδιο": f"{din:.1f}° {sign_el}",
                "Οίκος": house_of_degree(deg, houses) or "-",
                "Αναδρομή": "℞ Αναδρομικός" if is_r else "Ευθεία κίνηση",
            })
        st.dataframe(table_rows, use_container_width=True, hide_index=True, height=min(35 * (len(table_rows) + 1) + 3, 420))
        if retro_names:
            st.info("℞ Αναδρομικοί πλανήτες: " + ", ".join(retro_names))
        else:
            st.caption("Κανένας πλανήτης δεν είναι αναδρομικός σε αυτόν τον χάρτη.")
        try:
            from ephemeris_engine import LAST_ENGINE
            if LAST_ENGINE == "approx":
                st.warning("⚠️ Οι θέσεις των πλανητών είναι ΠΡΟΣΕΓΓΙΣΤΙΚΕΣ (δεν φόρτωσε η Swiss Ephemeris ούτε η εφεδρική μέθοδος). Μην βασίζεσαι σε αυτές.")
        except Exception:
            pass
        if aspects:
            if HAS_SAC:
                try:
                    colors = {
                        "Conjunction": "gold",
                        "Trine": "green",
                        "Sextile": "cyan",
                        "Square": "red",
                        "Opposition": "orange",
                    }
                    sac.tags(
                        [
                            sac.Tag(
                                f"{a['p1']} {a['aspect']} {a['p2']}",
                                color=colors.get(a["aspect"], "blue"),
                            )
                            for a in aspects[:8]
                        ],
                        align="start",
                    )
                except Exception:
                    st.caption(" · ".join(f"{a['p1']} {a['aspect']} {a['p2']}" for a in aspects[:8]))
            else:
                st.caption("Κύριες όψεις: " + " · ".join(
                    f"{a['p1']} {a['aspect']} {a['p2']}" for a in aspects[:8]
                ))
        
    with col2:
        st.subheader("📊 Βασικοί Δείκτες / Key Indicators")
        st.write(f"**Ημερομηνία / Date:** {b_date.strftime('%d/%m/%Y')} {b_time.strftime('%H:%M')} ({city_name_el} / {city_name_en})")
        
        # --- ΝΕΟ ΠΛΑΙΣΙΟ: Η ΑΣΤΡΟΛΟΓΙΚΗ ΤΡΙΑΔΑ ---
        sun_deg = natal_pos.get("Sun", 0.0)
        moon_deg = natal_pos.get("Moon", 0.0)
        asc_deg = houses.get("House_1", 0.0)
        
        sun_sign_en, _ = get_sign_from_degrees(sun_deg)
        moon_sign_en, _ = get_sign_from_degrees(moon_deg)
        asc_sign_en, _ = get_sign_from_degrees(asc_deg)
        
        sun_sign_el = ZODIAC_SIGNS.get(sun_sign_en, {}).get("el", sun_sign_en)
        moon_sign_el = ZODIAC_SIGNS.get(moon_sign_en, {}).get("el", moon_sign_en)
        asc_sign_el = ZODIAC_SIGNS.get(asc_sign_en, {}).get("el", asc_sign_en)

        st.markdown("""
        <div style="background-color: #1E293B; border-left: 4px solid #3B82F6; padding: 12px; border-radius: 6px; margin-bottom: 15px;">
            <h4 style="margin: 0 0 8px 0; color: #F8FAFC;">✨ Θεμελιώδης Τριάδα</h4>
            <p style="margin: 4px 0; color: #E2E8F0;">☀️ <b>Ήλιος:</b> {}</p>
            <p style="margin: 4px 0; color: #E2E8F0;">🌙 <b>Σελήνη:</b> {}</p>
            <p style="margin: 4px 0; color: #E2E8F0;">🌅 <b>Ωροσκόπος:</b> {}</p>
        </div>
        """.format(f"{sun_sign_el} ({sun_sign_en})", f"{moon_sign_el} ({moon_sign_en})", f"{asc_sign_el} ({asc_sign_en})"), unsafe_allow_html=True)

        st.info(f"🐉 **Κινεζικό Ζώδιο / Chinese Zodiac:** {cz_animal_bi} ({cz_element_bi})")
        
        elements_bilingual = {ELEMENT_TRANSLATIONS.get(k, k): v for k, v in elements_pct.items()}
        modalities_bilingual = {MODALITY_TRANSLATIONS.get(k, k): v for k, v in modalities_pct.items()}
        
        st.write("**Στοιχεία / Elements**")
        st.write(" · ".join([f"{k} {v}%" for k, v in elements_bilingual.items()]))
        st.write("**Ποιότητες / Modalities**")
        st.write(" · ".join([f"{k} {v}%" for k, v in modalities_bilingual.items()]))

        if prof_data.get("unknown_time"):
            st.warning("Η ώρα είναι άγνωστη — ο ωροσκόπος είναι προσεγγιστικός (ηλιακός χάρτης, 12:00).")
        
        with st.expander("💡 Πώς διαβάζονται τα Ποσοστά (%)", expanded=False):
            st.markdown("""
            * **Υψηλό Ποσοστό (π.χ. >30%):** Δείχνει το **κυρίαρχο στοιχείο/ποιότητα**. Εκεί διοχετεύεται αβίαστα η μεγαλύτερη ενέργεια του ατόμου.
            * **Χαμηλό Ποσοστό (π.χ. <15%):** Δείχνει έναν τομέα που χρειάζεται συνειδητή προσπάθεια και εξάσκηση για να ισορροπήσει.
            * **Στοιχεία:** Πυρ (Δράση/Πάθος), Γη (Σταθερότητα/Πρακτικότητα), Αέρας (Σκέψη/Επικοινωνία), Νερό (Συναίσθημα/Διαίσθηση).
            * **Ποιότητες:** Παρορμητικά (Πρωτοβουλία/Εκκίνηση), Σταθερά (Διατήρηση/Θεμελίωση), Μεταβλητά (Προσαρμογή/Εξέλιξη).
            """)
        
        with st.expander("🏠 Αιχμές 12 Οίκων / House Cusps (12)", expanded=False):
            houses_formatted = {}
            for h_num in range(1, 13):
                h_deg = houses.get(f"House_{h_num}", 0)
                sign_en, deg_in = get_sign_from_degrees(h_deg)
                sign_el = ZODIAC_SIGNS.get(sign_en, {}).get("el", sign_en)
                houses_formatted[f"Οίκος {h_num} / House {h_num}"] = f"{deg_in:.1f}° {sign_el} / {sign_en}"
            st.json(houses_formatted)

    st.markdown("---")
    st.subheader("🤖 AstroCaterpillar AI Analysis")
    
    fresh_ai = st.checkbox("🔄 Νέα εκδοχή ανάλυσης (αλλιώς εμφανίζεται πάντα η ίδια για τον ίδιο χάρτη)", value=False, key="fresh_ai")
    btn_ai = "🚀 Παραγωγή AI Ανάλυσης / Generate AI Analysis"
    if st.button(btn_ai):
        set_fresh(fresh_ai)
        with st.spinner("Ο AstroCaterpillar αναλύει τα δεδομένα... / Analyzing..."):
            pos_brief, asp_brief = format_chart_brief(natal_pos, houses, aspects, lang=lang)
            report = analyze_natal_chart_ai(
                selected_profile,
                pos_brief,
                str({k: houses[k] for k in houses if str(k).startswith("House_") or k in ("Asc", "MC")}),
                str(cz_data),
                f"Elements: {elements_pct}, Modalities: {modalities_pct}. " + (
                    ("Αναδρομικοί πλανήτες: " + ", ".join(retro_names)) if retro_names else "Κανένας πλανήτης αναδρομικός."),
                asp_brief,
                lang=lang
            )
            if str(report).startswith("⚠️"):
                try:
                    from local_report import build_local_natal
                    local_txt = build_local_natal(selected_profile, natal_pos, houses)
                    if local_txt:
                        report = ("ℹ️ Το AI δεν απάντησε αυτή τη στιγμή — ορίστε η βασική ανάλυση του χάρτη σου:\n\n"
                                  + local_txt)
                except Exception:
                    pass
            st.session_state[f"natal_ai_{selected_profile}_{lang}"] = report

    cache_key = f"natal_ai_{selected_profile}_{lang}"
    ai_report = st.session_state.get(cache_key)
    if ai_report:
        st.markdown(ai_report)
        st.download_button(
            label="📥 Download AI Report (.txt)",
            data=ai_report,
            file_name=f"AstroCaterpillar_Report_{selected_profile}.txt",
            mime="text/plain"
        )

    st.markdown("---")
    st.subheader("💬 Chat με τον AstroCaterpillar (Γενέθλιος Χάρτης)")
    if not ai_report:
        st.caption("Μπορείς να ρωτήσεις κατευθείαν — δεν χρειάζεται πρώτα η AI ανάλυση.")
    try:
        chat_context = ai_report or build_local_natal(selected_profile, natal_pos, houses)
    except Exception:
        chat_context = ""
    chat_context = (chat_context or "") + "\n\nΑναδρομικοί πλανήτες: " + (", ".join(retro_names) if retro_names else "κανένας")

    natal_chat_key = chat_bucket("natal", selected_profile)
    quick_q = quick_buttons("natal", [
        ("℞ Αναδρομικοί", "Τι σημαίνουν οι αναδρομικοί πλανήτες στον χάρτη μου και πώς με επηρεάζουν στην καθημερινότητα; Δώσε απλά παραδείγματα."),
        ("💕 Αγάπη", "Πώς είμαι στις σχέσεις και στον έρωτα; Τι χρειάζομαι και τι πρέπει να προσέχω; Δώσε συγκεκριμένα παραδείγματα."),
        ("💼 Καριέρα", "Ποιες δουλειές και τρόποι δουλειάς μου ταιριάζουν και πώς να προχωρήσω επαγγελματικά και οικονομικά;"),
        ("📅 Αυτός ο μήνας", "__MONTH__"),
        ("💪 Δυνατά/αδύνατα", "Ποια είναι τα 3 δυνατά και τα 3 αδύνατα σημεία μου; Απάντησε απλά με παραδείγματα."),
    ])
    if quick_q == "__MONTH__":
        _today = datetime.date.today()
        try:
            _pts = dict(natal_pos)
            _pts["Asc"], _pts["MC"] = houses.get("Asc", 0.0), houses.get("MC", 0.0)
            _w = cached_transit_windows(tuple(sorted(_pts.items())), _today.replace(day=1).isoformat(), 60)
            _mb = month_brief(_w, _today.year, _today.month)
        except Exception:
            _mb = "άγνωστες"
        quick_q = (f"Τι να περιμένω αυτόν τον μήνα ({_today.month}/{_today.year}); "
                   f"Βασικές διελεύσεις προς τον χάρτη μου: {_mb}. Απάντησε απλά και πρακτικά.")

    for msg in st.session_state.chat_history[natal_chat_key]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_q = st.chat_input("Κάνε μια ερώτηση πάνω στον γενέθλιο χάρτη σου...") or quick_q
    if user_q:
        st.session_state.chat_history[natal_chat_key].append({"role": "user", "content": user_q})
        with st.spinner("Σκέφτεται... / Thinking..."):
            history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[natal_chat_key]])
            full_prompt = f"Ανάλυση / στοιχεία χάρτη:\n{chat_context}\n\nΙστορικό Συζήτησης:\n{history_text}\n\nΤελευταία Ερώτηση: {user_q}"
            ans = ask_caterpillar_chat(chat_context, full_prompt, lang=lang)
            st.session_state.chat_history[natal_chat_key].append({"role": "assistant", "content": ans})
            st.rerun()

# --- TAB 2: MONTHLY TRANSITS ---
elif menu_choice.startswith("2."):
    st.header(f"📅 Μηνιαίες Διελεύσεις / Monthly Transits: {selected_profile}")
    
    col_t1, col_t2 = st.columns(2)
    
    months_bilingual = [
        "Ιανουάριος / January", "Φεβρουάριος / February", "Μάρτιος / March",
        "Απρίλιος / April", "Μάιος / May", "Ιούνιος / June",
        "Ιούλιος / July", "Αύγουστος / August", "Σεπτέμβριος / September",
        "Οκτώβριος / October", "Νοέμβριος / November", "Δεκέμβριος / December"
    ]
    
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    
    with col_t1:
        sel_month_name = st.selectbox("Επιλογή Μήνα / Select Month:", months_bilingual, index=current_month - 1)
        sel_month_num = months_bilingual.index(sel_month_name) + 1
    with col_t2:
        sel_year = st.number_input("Επιλογή Έτους / Select Year:", min_value=2024, max_value=2035, value=current_year)
    
    timeframe_label = f"{sel_month_name} {sel_year}"
    
    # --- ΤΟΠΙΚΕΣ ΔΙΕΛΕΥΣΕΙΣ (χωρίς AI) ---
    _t_city = GREEK_AND_WORLD_CITIES.get(prof_data["city"], {})
    _t_tz = _t_city.get("tz", "Europe/Athens")
    _t_houses = safe_houses(
        prof_data["date"].year, prof_data["date"].month, prof_data["date"].day,
        prof_data["time"].hour + prof_data["time"].minute / 60.0,
        _t_city.get("lat", 37.9838), _t_city.get("lon", 23.7275), tz_name=_t_tz,
    )
    _t_pts = {p: extract_deg(v) for p, v in prof_data["positions"].items()}
    _t_pts["Asc"], _t_pts["MC"] = _t_houses.get("Asc", 0.0), _t_houses.get("MC", 0.0)
    _t_start = datetime.date.today()
    st.subheader("🔭 Τι έρχεται τους επόμενους 6 μήνες (χωρίς AI)")
    with st.spinner("Υπολογίζω τις διελεύσεις… την πρώτη φορά κάνει λίγο, μετά είναι άμεσο."):
        local_windows = cached_transit_windows(tuple(sorted(_t_pts.items())), _t_start.isoformat(), 180)
    local_md = monthly_summary_markdown(local_windows, _t_start, months=6)
    st.markdown(local_md)
    st.caption("Υπολογισμός με τη μηχανή θέσεων της εφαρμογής: Άρης, Δίας, Κρόνος, Ουρανός, Ποσειδώνας, Πλούτωνας προς τα γενέθλια σημεία σου. Οι ημερομηνίες είναι κατά προσέγγιση (±1-2 ημέρες).")
    st.download_button("📥 Κατέβασμα (.txt)", data=local_md, file_name=f"Transits_6m_{selected_profile}.txt", mime="text/plain")
    st.markdown("---")
    st.subheader("🤖 Ανάλυση AI για συγκεκριμένο μήνα")

    if st.button("🔮 Στρατηγική Ανάλυση Μήνα / Analyze Monthly Trends"):
        with st.spinner("Υπολογισμός Μακρο-Κύκλων... / Calculating Macro Cycles..."):
            natal_degrees = {p: extract_deg(v) for p, v in prof_data["positions"].items()}
            m_transits = calculate_monthly_transits(natal_degrees, sel_year, sel_month_num)
            report = analyze_transits_ai(selected_profile, timeframe_label, str(m_transits), lang=lang)
            st.session_state[f"transits_ai_{selected_profile}_{sel_month_num}_{sel_year}_{lang}"] = report

    t_cache_key = f"transits_ai_{selected_profile}_{sel_month_num}_{sel_year}_{lang}"
    ai_tr = st.session_state.get(t_cache_key)
    if ai_tr:
        st.markdown(ai_tr)
        st.download_button(
            label="📥 Download Transits Report (.txt)",
            data=ai_tr,
            file_name=f"Transits_Report_{selected_profile}_{sel_month_num}_{sel_year}.txt",
            mime="text/plain"
        )

    st.markdown("---")
    st.subheader("💬 Chat με τον AstroCaterpillar (Διελεύσεις)")
    report_text = ai_tr or ("Διελεύσεις επόμενων μηνών (τοπικός υπολογισμός):\n" + local_md)
    tr_chat_key = chat_bucket("transits", f"{selected_profile}:{sel_month_num}:{sel_year}")
    _mbrief = month_brief(local_windows, int(sel_year), sel_month_num)
    quick_t = quick_buttons("transits", [
        ("📅 Αυτός ο μήνας", f"Τι να περιμένω τον μήνα {timeframe_label}; Βασικές διελεύσεις: {_mbrief}. Απάντησε απλά και πρακτικά."),
        ("💕 Αγάπη", f"Τι σημαίνουν οι διελεύσεις του μήνα {timeframe_label} για τις σχέσεις μου; Διελεύσεις: {_mbrief}."),
        ("💼 Καριέρα/χρήματα", f"Τι σημαίνουν οι διελεύσεις του μήνα {timeframe_label} για δουλειά και χρήματα; Διελεύσεις: {_mbrief}."),
        ("⚠️ Τι να προσέξω", f"Τι να προσέξω τον μήνα {timeframe_label}; Διελεύσεις: {_mbrief}. Δώσε 3 πρακτικές συμβουλές."),
    ])
    for msg in st.session_state.chat_history[tr_chat_key]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_q = st.chat_input("Κάνε μια ερώτηση πάνω στις διελεύσεις του μήνα...") or quick_t
    if user_q:
        st.session_state.chat_history[tr_chat_key].append({"role": "user", "content": user_q})
        with st.spinner("Σκέφτεται... / Thinking..."):
            history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[tr_chat_key]])
            full_prompt = f"Ανάλυση Διελεύσεων ({timeframe_label}):\n{report_text}\n\nΙστορικό Συζήτησης:\n{history_text}\n\nΤελευταία Ερώτηση: {user_q}"
            ans = ask_caterpillar_chat(report_text, full_prompt, lang=lang)
            st.session_state.chat_history[tr_chat_key].append({"role": "assistant", "content": ans})
            st.rerun()

# --- TAB 3: SYNASTRY ---
# --- TAB 3: SYNASTRY ---
elif menu_choice.startswith("3."):
    st.header("💞 Συναστρία / Synastry")
    
    if len(profile_names) < 2:
        st.warning("Απαιτούνται τουλάχιστον 2 προφίλ / At least 2 profiles required.")
    else:
        p1 = st.selectbox("Πρώτο Άτομο / Person 1:", profile_names, index=0)
        p2 = st.selectbox("Δεύτερο Άτομο / Person 2:", profile_names, index=1 if len(profile_names) > 1 else 0)
        
        if p1 != p2:
            if st.button("💖 Υπολογισμός Συναστρίας / Calculate Synastry"):
                pos1 = {p: extract_deg(v) for p, v in saved_profiles[p1]["positions"].items()}
                pos2 = {p: extract_deg(v) for p, v in saved_profiles[p2]["positions"].items()}
                syn_aspects = calculate_synastry_aspects(pos1, pos2)
                
                # Διαδραστικό Plotly Χάρτης Συναστρίας (Hover/Touch)
                syn_fig = create_interactive_synastry_plotly(pos1, pos2, name1=p1, name2=p2, lang=lang)
                st.plotly_chart(syn_fig, use_container_width=True)
                
                with st.spinner("Ανάλυση... / Analyzing..."):
                    report = analyze_synastry_ai(p1, p2, str(syn_aspects), lang=lang)
                    st.session_state[f"synastry_ai_{p1}_{p2}_{lang}"] = report

            s_cache_key = f"synastry_ai_{p1}_{p2}_{lang}"
            if s_cache_key in st.session_state:
                report_text = st.session_state[s_cache_key]
                st.markdown(report_text)
                
                st.download_button(
                    label="📥 Download Synastry Report (.txt)",
                    data=report_text,
                    file_name=f"Synastry_Report_{p1}_{p2}.txt",
                    mime="text/plain"
                )

                st.markdown("---")
                if st.button("📚 Εξαγωγή Synastry Ebook (PDF)"):
                    with st.spinner("Σύνθεση Ebook... / Building Ebook..."):
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
                
                st.markdown("---")
                st.subheader("💬 Chat με τον AstroCaterpillar (Συναστρία)")
                
                sy_chat_key = chat_bucket("synastry", f"{p1}|{p2}")
                for msg in st.session_state.chat_history[sy_chat_key]:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
                        
                user_q = st.chat_input("Κάνε μια ερώτηση πάνω στη συναστρία των δύο ατόμων...")
                if user_q:
                    st.session_state.chat_history[sy_chat_key].append({"role": "user", "content": user_q})
                    with st.spinner("Σκέφτεται... / Thinking..."):
                        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[sy_chat_key]])
                        full_prompt = f"Αρχική Ανάλυση Συναστρίας ({p1} & {p2}):\n{report_text}\n\nΙστορικό Συζήτησης:\n{history_text}\n\nΤελευταία Ερώτηση: {user_q}"
                        ans = ask_caterpillar_chat(report_text, full_prompt, lang=lang)
                        st.session_state.chat_history[sy_chat_key].append({"role": "assistant", "content": ans})
                        st.rerun()

# --- TAB 4: EXPORT PDF ---
elif menu_choice.startswith("4."):
    st.header(f"📥 Εξαγωγή PDF / PDF Export: {selected_profile}")
    
    col_a, col_b = st.columns(2)
    natal_degrees = {p: extract_deg(v) for p, v in prof_data["positions"].items()}
    
    with col_a:
        st.subheader("📄 One-Pager Summary")
        if st.button("📥 Download One-Pager (PDF)"):
            with st.spinner("Δημιουργία... / Generating..."):
                from ephemeris_engine import retro_planets
                _ex_date, _ex_time = prof_data["date"], prof_data["time"]
                _tz = GREEK_AND_WORLD_CITIES.get(prof_data["city"], {}).get("tz", "Europe/Athens")
                _retro_en = retro_planets(prof_data["positions"], _ex_date.year, _ex_date.month, _ex_date.day,
                                          _ex_time.hour + _ex_time.minute / 60.0, _tz)
                _retro_el = [PLANET_TRANSLATIONS.get(p, {}).get("el", p) for p in _retro_en]
                retro_line = ("Αναδρομικοί πλανήτες: " + ", ".join(_retro_el)) if _retro_el else "Κανένας πλανήτης αναδρομικός."
                one_pager_text = st.session_state.get(f"natal_ai_{selected_profile}_{lang}", "Δεν έχει παραχθεί AI ανάλυση.")
                one_pager_text += f"\n\n### ℞ Αναδρομικότητα\n{retro_line}"
                _hist = st.session_state.chat_history.get(chat_bucket("natal", selected_profile), [])
                if _hist:
                    one_pager_text += "\n\n### Ερωτήσεις & Απαντήσεις AI\n" + "\n\n".join(
                        ("**Ερώτηση:** " if m["role"] == "user" else "**AI:** ") + str(m["content"]) for m in _hist[-6:])
                fig, ax = plt.subplots(figsize=(5, 5), facecolor='#121824', subplot_kw={'projection': 'polar'})
                plot_natal_chart(ax, natal_degrees)
                
                pdf_bytes = create_astrology_pdf(
                    "AstroCaterpillar Summary",
                    selected_profile,
                    f"Date: {prof_data['date'].strftime('%d/%m/%Y')} | City: {prof_data['city']}",
                    fig_mat=fig,
                    summary_info=f"Positions: {str(natal_degrees)} | " + retro_line,
                    ai_summary_text=one_pager_text,
                    lang=lang
                )
                st.download_button("Download PDF", pdf_bytes, file_name=f"{selected_profile}_summary.pdf", mime="application/pdf")
                
    with col_b:
        st.subheader("📚 Executive Ebook")
        if st.button("📥 Download Ebook (PDF)"):
            with st.spinner("Σύνθεση Ebook... / Building Ebook..."):
                ebook_bytes = create_full_astrology_ebook(selected_profile, prof_data, lang=lang)
                st.download_button("Download Ebook PDF", ebook_bytes, file_name=f"{selected_profile}_Ebook.pdf", mime="application/pdf")

# --- TAB 5: ASTROLOGY GUIDE ---
elif menu_choice.startswith("5."):
    st.header("📚 Οδηγός Αστρολογίας / Astrology Guide")
    st.markdown("Χρησιμοποιήστε τους παρακάτω πίνακες ως οδηγό αναφοράς για τη σημασία των 12 Οίκων, των 12 Ζωδίων, των Ανάδρομων Πλανητών, των Στοιχείων και των Πιοτήτων.")
    
    col_g1, col_g2, col_g3 = st.columns(3)
    
    with col_g1:
        st.subheader("🏠 Οι 12 Οίκοι")
        for house_title, house_desc in HOUSES_GUIDE.items():
            with st.expander(house_title):
                st.write(house_desc)
                
    with col_g2:
        st.subheader("♈ Τα 12 Ζώδια")
        for zodiac_title, zodiac_desc in ZODIAC_GUIDE.items():
            with st.expander(zodiac_title):
                st.write(zodiac_desc)

    with col_g3:
        st.subheader("🔄 Ανάδρομοι Πλανήτες (R)")
        for retro_title, retro_desc in RETROGRADE_GUIDE.items():
            with st.expander(retro_title):
                st.write(retro_desc)

    st.markdown("---")
    
    col_g4, col_g5 = st.columns(2)
    
    with col_g4:
        st.subheader("🧪 Τα 4 Στοιχεία / Elements")
        for elem_title, elem_desc in ELEMENTS_GUIDE.items():
            with st.expander(elem_title):
                st.write(elem_desc)
                
    with col_g5:
        st.subheader("⚖️ Οι 3 Ποιότητες / Modalities")
        for mod_title, mod_desc in MODALITIES_GUIDE.items():
            with st.expander(mod_title):
                st.write(mod_desc)

# --- TAB 6: ADMIN PANEL ---
elif menu_choice.startswith("6."):
    st.header("⚙️ Admin Panel")
    
    if not st.session_state.is_admin:
        admin_pass = st.text_input("Κωδικός Πρόσβασης / Admin Password:", type="password")
        if st.button("Σύνδεση ως Admin / Login"):
            from ai_engine import _secret
            expected_admin = _secret("ADMIN_PASSWORD")
            if not expected_admin:
                st.error("Δεν έχει οριστεί ADMIN_PASSWORD στα Secrets.")
            elif admin_pass and admin_pass == expected_admin:
                st.session_state.is_admin = True
                st.success("Πρόσβαση εγκρίθηκε! / Access Granted!")
                st.rerun()
            else:
                st.error("Λανθασμένος κωδικός / Incorrect Password.")
    else:
        st.success("Είστε συνδεδεμένος ως Admin / Logged in as Admin!")
        db_profiles = load_profiles_from_db()
        st.write(f"**Μόνιμα Αποθηκευμένα Προφίλ στη Βάση:** {len(db_profiles)}")
        st.info(st.session_state.get("backup_status", "Δεν έχει γίνει ακόμα συγχρονισμός backup σε αυτή τη συνεδρία."))
        if _backup_token():
            if st.button("☁️ Αποθήκευση τώρα στο GitHub backup"):
                sync_backup()
                st.rerun()
        else:
            st.caption("Για αυτόματο backup πρόσθεσε στα Secrets: GITHUB_TOKEN (token με δικαίωμα «gist»). "
                       "Αλλιώς κατέβασε το JSON παρακάτω και ανέβασέ το στο repo ως profiles_backup.json.")
        
        st.markdown("---")
        st.subheader("📦 Διαχείριση, Backup & Εισαγωγή Βάσης / Database Management")
        
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            st.markdown("##### 1. Εξαγωγή / Export")
            json_data = export_db_as_json()
            st.download_button(
                label="📥 Download Database (JSON)",
                data=json_data,
                file_name=f"astro_profiles_backup_{datetime.date.today()}.json",
                mime="application/json"
            )
            
            try:
                with open(DB_FILE, "rb") as fp:
                    db_bytes = fp.read()
                st.download_button(
                    label="📥 Download Database (.db)",
                    data=db_bytes,
                    file_name="astro_data.db",
                    mime="application/x-sqlite3"
                )
            except Exception:
                pass

        with col_dl2:
            st.markdown("##### 2. Εισαγωγή / Import JSON")
            uploaded_json = st.file_uploader("Ανεβάστε αρχείο JSON / Upload JSON file:", type=["json"])
            if uploaded_json is not None:
                if st.button("📤 Εισαγωγή Προφίλ / Import Profiles"):
                    try:
                        content = uploaded_json.read().decode("utf-8")
                        count = import_db_from_json(content)
                        st.success(f"Εισήχθησαν {count} προφίλ! / Imported {count} profiles!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Σφάλμα / Error: {str(e)}")

        st.markdown("---")
        col_adm1, col_adm2 = st.columns(2)
        with col_adm1:
            if st.button("🧹 Καθαρισμός AI Cache / Clear AI Cache"):
                clear_ai_cache()
                st.session_state.chat_history = {}
                st.success("Η AI Cache και το ιστορικό Chat καθαρίστηκαν!")
        with col_adm2:
            if st.button("🚪 Αποσύνδεση Admin / Logout"):
                st.session_state.is_admin = False
                st.rerun()
