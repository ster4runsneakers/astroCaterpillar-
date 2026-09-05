# ai_engine.py - Direct REST API (Zero SDK Compatibility Issues)
import os
import requests
import Streamlit as st

SYSTEM_PROMPT = (
    "Είσαι ένας έμπειρος, ζεστός, επικοινωνιακός και βαθιά αφηγηματικός αστρολόγος, στο ύφος της Ισμήνης Καράλη και της Λίτσας Πατέρα. "
    "Ο λόγος σου είναι γλαφυρός, συναισθηματικός και ενθαρρυντικός. "
    "ΥΠΟΧΡΕΩΤΙΚΑ ενσωματώνεις στις αναλύσεις σου στοιχεία από την ελληνική μυθολογία, την ιστορία και τα αρχαία αρχέτυπα, "
    "συνδέοντας τους πλανήτες και τις όψεις με αλληγορίες. "
    "ΑΠΑΓΟΡΕΥΟΝΤΑΙ οι ψυχρές λίστες με μοίρες. ΟΦΕΙΛΕΙΣ να ερμηνεύεις και να συνθέτεις τα δεδομένα."
)

def _get_api_key(user_api_key=""):
    clean_user_key = user_api_key.strip() if user_api_key else ""
    return clean_user_key if (clean_user_key and not clean_user_key.startswith("sk-")) else st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "")).strip()

def _run_direct_rest_call(prompt: str, user_api_key: str = ""):
    api_key = _get_api_key(user_api_key)
    if not api_key:
        return "⚠️ Δεν βρέθηκε έγκυρο GEMINI_API_KEY στα Secrets."

    # Δοκιμή σταθερών μοντέλων v1beta / v1
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
    last_err = ""

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 2048,
                "temperature": 0.7
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            res_data = response.json()
            
            if response.status_code == 200:
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            else:
                last_err = res_data.get("error", {}).get("message", response.text)
        except Exception as e:
            last_err = str(e)
            continue

    return f"⚠️ Στιγμιαία καθυστέρηση απόκρισης. Παρακαλώ πατήστε ξανά το κουμπί σε 2-3 δευτερόλεπτα.\n*(Log: {last_err})*"

def analyze_natal_chart_ai_stream(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    # Fallback generator για συμβατότητα με το st.write_stream
    res = analyze_natal_chart_ai(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang, user_api_key)
    yield res

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
    return _run_direct_rest_call(prompt, user_api_key)

@st.cache_data(ttl=86400, show_spinner=False)
def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    prompt = f"Πρόβλεψη διελεύσεων για '{profile_name}' ({timeframe}): {transits_data}"
    return _run_direct_rest_call(prompt, user_api_key)

@st.cache_data(ttl=86400, show_spinner=False)
def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    prompt = f"Ανάλυση συναστρίας ανάμεσα σε '{p1}' και '{p2}': {synastry_aspects}"
    return _run_direct_rest_call(prompt, user_api_key)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    prompt = f"Πλαίσιο:\n{context_text}\n\nΕρώτηση: {user_prompt}"
    return _run_direct_rest_call(prompt, user_api_key)

def clear_ai_cache():
    st.cache_data.clear()
