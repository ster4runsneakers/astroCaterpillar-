# ai_engine.py - Clean Gemini Direct Engine (No Deadlocks)
import os
import streamlit as st
from google import genai

SYSTEM_PROMPT = (
    "Είσαι ένας έμπειρος, ζεστός, επικοινωνιακός και βαθιά αφηγηματικός αστρολόγος, στο ύφος της Ισμήνης Καράλη και της Λίτσας Πατέρα. "
    "Ο λόγος σου είναι γλαφυρός, συναισθηματικός και ενθαρρυντικός. "
    "ΥΠΟΧΡΕΩΤΙΚΑ ενσωματώνεις στις αναλύσεις σου στοιχεία από την ελληνική μυθολογία, την ιστορία και τα αρχαία αρχέτυπα, "
    "συνδέοντας τους πλανήτες και τις όψεις με αλληγορίες. "
    "ΑΠΑΓΟΡΕΥΟΝΤΑΙ οι ψυχρές λίστες με μοίρες. ΟΦΕΙΛΕΙΣ να ερμηνεύεις και να συνθέτεις τα δεδομένα."
)

def _get_gemini_client(user_api_key=""):
    clean_user_key = user_api_key.strip() if user_api_key else ""
    if clean_user_key and not clean_user_key.startswith("sk-"):
        return genai.Client(api_key=clean_user_key)
    
    master_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "")).strip()
    if master_key:
        return genai.Client(api_key=master_key)
    return None

def _generate_unified_response(prompt: str, user_api_key: str = ""):
    gem_client = _get_gemini_client(user_api_key)
    
    if not gem_client:
        return "⚠️ Δεν βρέθηκε έγκυρο GEMINI_API_KEY στα Secrets του Streamlit."

    # Ενεργά μοντέλα βάσει των τελευταίων οδηγιών της Google
    active_models = [
        'gemini-3.1-pro-preview',
        'gemini-3.6-flash',
        'gemini-2.5-flash'
    ]
    
    full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
    last_errors = []

    for g_model in active_models:
        try:
            resp = gem_client.models.generate_content(
                model=g_model,
                contents=full_prompt
            )
            if resp and resp.text:
                return resp.text
        except Exception as e:
            last_errors.append(f"{g_model}: {str(e)}")
            continue

    err_msg = " | ".join(last_errors) if last_errors else "Άγνωστο σφάλμα."
    return f"⚠️ Στιγμιαίος φόρτος στις υποδομές της Google. Παρακαλώ πατήστε ξανά το κουμπί σε λίγα δευτερόλεπτα.\n*(Log: {err_msg})*"

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
    return _generate_unified_response(prompt, user_api_key)

def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    prompt = f"Ανάλυση διελεύσεων για '{profile_name}' ({timeframe}): {transits_data}"
    return _generate_unified_response(prompt, user_api_key)

def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    prompt = f"Ανάλυση συναστρίας {p1} & {p2}: {synastry_aspects}"
    return _generate_unified_response(prompt, user_api_key)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    prompt = f"Πλαίσιο: {context_text}\nΕρώτηση: {user_prompt}"
    return _generate_unified_response(prompt, user_api_key)

def clear_ai_cache():
    pass
