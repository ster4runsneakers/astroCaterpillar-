# ai_engine.py - Bulletproof Model Selection
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
        yield "⚠️ Δεν βρέθηκε έγκυρο GEMINI_API_KEY."
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

    # Δοκιμή αποκλειστικά των νέων Flash μοντέλων
    for m_name in ['gemini-2.5-flash', 'gemini-2.0-flash']:
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

    yield "⚠️ Στιγμιαία καθυστέρηση απόκρισης. Παρακαλώ δοκιμάστε ξανά."

def _run_genai_call(prompt: str, user_api_key: str = ""):
    client = _get_client(user_api_key)
    if not client:
        return "⚠️ Δεν βρέθηκε έγκυρο GEMINI_API_KEY."

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        max_output_tokens=2048,
        temperature=0.7
    )

    last_err = ""
    for m_name in ['gemini-2.5-flash', 'gemini-2.0-flash']:
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
            continue

    return f"⚠️ Στιγμιαία καθυστέρηση απόκρισης. Παρακαλώ πατήστε ξανά το κουμπί.\n*(Log: {last_err})*"

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
    prompt = f"Πρόβλεψη διελεύσεων για '{profile_name}' ({timeframe}): {transits_data}"
    return _run_genai_call(prompt, user_api_key)

@st.cache_data(ttl=86400, show_spinner=False)
def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    prompt = f"Ανάλυση συναστρίας ανάμεσα σε '{p1}' και '{p2}': {synastry_aspects}"
    return _run_genai_call(prompt, user_api_key)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    prompt = f"Πλαίσιο:\n{context_text}\n\nΕρώτηση: {user_prompt}"
    return _run_genai_call(prompt, user_api_key)

def clear_ai_cache():
    st.cache_data.clear()
