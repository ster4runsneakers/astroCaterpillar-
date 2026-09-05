# ai_engine.py - Complete Protected & Cached Engine
import os
import time
import streamlit as st
import google.generativeai as genai

SYSTEM_PROMPT = (
    "Είσαι ένας έμπειρος, ζεστός, επικοινωνιακός και βαθιά αφηγηματικός αστρολόγος, στο ύφος της Ισμήνης Καράλη και της Λίτσας Πατέρα. "
    "Ο λόγος σου είναι γλαφυρός, συναισθηματικός και ενθαρρυντικός. "
    "ΥΠΟΧΡΕΩΤΙΚΑ ενσωματώνεις στις αναλύσεις σου στοιχεία από την ελληνική μυθολογία, την ιστορία και τα αρχαία αρχέτυπα, "
    "συνδέοντας τους πλανήτες και τις όψεις με αλληγορίες. "
    "ΑΠΑΓΟΡΕΥΟΝΤΑΙ οι ψυχρές λίστες με μοίρες. ΟΦΕΙΛΕΙΣ να ερμηνεύεις και να συνθέτεις τα δεδομένα."
)

def _configure_gemini(user_api_key=""):
    clean_user_key = user_api_key.strip() if user_api_key else ""
    key = clean_user_key if (clean_user_key and not clean_user_key.startswith("sk-")) else st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "")).strip()
    if key:
        genai.configure(api_key=key)
        return True
    return False

def _run_cached_gemini_call(prompt: str, user_api_key: str = ""):
    if not _configure_gemini(user_api_key):
        return "⚠️ Δεν βρέθηκε έγκυρο GEMINI_API_KEY."

    generation_config = genai.GenerationConfig(
        max_output_tokens=2048,
        temperature=0.7
    )

    free_models = ['gemini-2.5-flash', 'gemini-1.5-flash']
    
    for model_name in free_models:
        try:
            model = genai.GenerativeModel(model_name, generation_config=generation_config)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            if "503" in str(e):
                time.sleep(1.0)
                continue
            continue

    return "⚠️ Στιγμιαίος φόρτος στις υποδομές AI. Παρακαλώ δοκιμάστε ξανά σε λίγα δευτερόλεπτα."

# --- NATAL CHART CACHING ---
@st.cache_data(ttl=86400, show_spinner=False)
def analyze_natal_chart_ai(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    prompt = f"""
    {SYSTEM_PROMPT}

    Κάνε μια αναλυτική, ζεστή, γλαφυρή και βαθιά αστρολογική ανάλυση για το γενέθλιο προφίλ '{profile_name}', στο ύφος της Ισμήνης Καράλη και της Λίτσας Πατέρα.

    ΔΕΔΟΜΕΝΑ ΧΑΡΤΗ:
    - Θέσεις Πλανητών: {raw_positions}
    - Οίκοι: {houses}
    - Κινεζικό Ζώδιο: {cz_data}
    - Στοιχεία & Ποιότητες: {indicators}
    - Όψεις: {aspects}

    ΟΔΗΓΙΕΣ ΣΥΝΤΑΞΗΣ & ΥΦΟΥΣ:
    1. ΜΗΝ ξεκινάς παραθέτοντας απλώς τη λίστα Ήλιου/Σελήνης/Ωροσκόπου.
    2. ΠΛΕΞΕ στην ανάλυση μυθολογικούς συμβολισμούς και ιστορικές αλληγορίες που ταιριάζουν στις κυρίαρχες όψεις του χάρτη.
    3. Χώρισε την ανάλυση σε:
       - **Ψυχικός Πυρήνας & Αρχέτυπα (Προσωπικότητα)**
       - **Συναισθηματικά Μονοπάτια & Έρωτας**
       - **Πορεία Πεπρωμένου, Καριέρα & Ευκαιρίες**
    4. Γράψε σε άπταιστα Ελληνικά.
    """
    return _run_cached_gemini_call(prompt, user_api_key)

# --- TRANSITS CACHING ---
@st.cache_data(ttl=86400, show_spinner=False)
def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    prompt = f"""
    {SYSTEM_PROMPT}

    Κάνε μια αναλυτική πρόβλεψη διελεύσεων για το προφίλ '{profile_name}' για τη χρονική περίοδο '{timeframe}'.
    Δεδομένα Διελεύσεων: {transits_data}

    Σύνθεσε τις επιδράσεις των πλανητών με γλαφυρό τρόπο, χρησιμοποιώντας αλληγορίες και εστιάζοντας σε ευκαιρίες, προκλήσεις και ψυχολογική εξέλιξη.
    """
    return _run_cached_gemini_call(prompt, user_api_key)

# --- SYNASTRY CACHING ---
@st.cache_data(ttl=86400, show_spinner=False)
def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    prompt = f"""
    {SYSTEM_PROMPT}

    Κάνε μια αναλυτική ανάλυση συναστρίας και χημικής αλληλεπίδρασης ανάμεσα στα άτομα '{p1}' και '{p2}'.
    Όψεις Συναστρίας: {synastry_aspects}

    Ανάλυσε τη συναισθηματική σύνδεση, τα σημεία τριβής και τη μυθολογική αλληγορία της σχέσης τους.
    """
    return _run_cached_gemini_call(prompt, user_api_key)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    prompt = f"{SYSTEM_PROMPT}\n\nΠλαίσιο:\n{context_text}\n\nΕρώτηση Χρήστη: {user_prompt}"
    return _run_cached_gemini_call(prompt, user_api_key)

def clear_ai_cache():
    st.cache_data.clear()
