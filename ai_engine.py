# ai_engine.py - Complete GenAI Engine
import os
import time
import streamlit as st
from google import genai
from google.genai import types

SYSTEM_PROMPT = (
    "Είσαι ένας έμπειρος, ζεστός, επικοινωνιακός και βαθιά αφηγηματικός αστρολόγος, στο ύφος της Ισμήνης Καράλη και της Λίτσας Πατέρα. "
    "Ο λόγος σου είναι γλαφυρός, συναισθηματικός και ενθαρρυντικός. "
    "ΥΠΟΧΡΕΩΤΙΚΑ ενσωματώνεις στις αναλύσεις σου στοιχεία από την ελληνική μυθολογία, την ιστορία και τα αρχαία αρχέτυπα, "
    "συνδέοντας τους πλανήτες και τις όψεις με αλληγορίες. "
    "ΑΠΑΓΟΡΕΥΟΝΤΑΙ οι ψυχρές λίστες με μοίρες. ΟΦΕΙΛΕΙΣ να ερμηνεύεις και να συνθέτεις τα δεδομένα."
)

def _get_client(user_api_key=""):
    clean_user_key = user_api_key.strip() if user_api_key else ""
    key = clean_user_key if (clean_user_key and not clean_user_key.startswith("sk-")) else st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "")).strip()
    if key:
        return genai.Client(api_key=key)
    return None

def analyze_natal_chart_ai_stream(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    client = _get_client(user_api_key)
    if not client:
        yield "⚠️ Δεν βρέθηκε έγκυρο GEMINI_API_KEY στα Secrets."
        return

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        max_output_tokens=2048,
        temperature=0.7
    )

    prompt = f"""
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

    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash']

    for m_name in models_to_try:
        try:
            response = client.models.generate_content_stream(
                model=m_name,
                contents=prompt,
                config=config
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            return
        except Exception:
            continue

    yield "⚠️ Στιγμιαία καθυστέρηση απόκρισης από τις υποδομές AI. Παρακαλώ δοκιμάστε ξανά."

def _run_genai_call(prompt: str, user_api_key: str = ""):
    client = _get_client(user_api_key)
    if not client:
        return "⚠️ Δεν βρέθηκε έγκυρο GEMINI_API_KEY στα Secrets."

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        max_output_tokens=2048,
        temperature=0.7
    )

    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash']
    last_err = ""

    for m_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=m_name,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_err = str(e)
                if "503" in last_err or "429" in last_err:
                    time.sleep(1.0)
                    continue
                break

    return f"⚠️ Στιγμιαία καθυστέρηση απόκρισης. Παρακαλώ πατήστε ξανά το κουμπί σε 2-3 δευτερόλεπτα.\n*(Log: {last_err})*"

# --- CACHED FUNCTIONS ---
@st.cache_data(ttl=86400, show_spinner=False)
def analyze_natal_chart_ai(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    prompt = f"""
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
    return _run_genai_call(prompt, user_api_key)

@st.cache_data(ttl=86400, show_spinner=False)
def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    prompt = f"""
    Κάνε μια αναλυτική πρόβλεψη διελεύσεων για το προφίλ '{profile_name}' για τη χρονική περίοδο '{timeframe}'.
    Δεδομένα Διελεύσεων: {transits_data}

    Σύνθεσε τις επιδράσεις των πλανητών με γλαφυρό τρόπο, χρησιμοποιώντας αλληγορίες και εστιάζοντας σε ευκαιρίες, προκλήσεις και ψυχολογική εξέλιξη.
    """
    return _run_genai_call(prompt, user_api_key)

@st.cache_data(ttl=86400, show_spinner=False)
def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    prompt = f"""
    Κάνε μια αναλυτική ανάλυση συναστρίας και χημικής αλληλεπίδρασης ανάμεσα στα άτομα '{p1}' και '{p2}'.
    Όψεις Συναστρίας: {synastry_aspects}

    Ανάλυσε τη συναισθηματική σύνδεση, τα σημεία τριβής και τη μυθολογική αλληγορία της σχέσης τους.
    """
    return _run_genai_call(prompt, user_api_key)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    prompt = f"Πλαίσιο Αρχικής Ανάλυσης:\n{context_text}\n\nΕρώτηση Χρήστη: {user_prompt}"
    return _run_genai_call(prompt, user_api_key)

def clear_ai_cache():
    st.cache_data.clear()
