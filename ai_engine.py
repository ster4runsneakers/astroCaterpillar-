# ai_engine.py - Stream-Enabled Engine
import os
import time
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

def analyze_natal_chart_ai_stream(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    """
    Generator function που επιστρέφει το κείμενο κομμάτι-κομμάτι (streaming) 
    για να εμφανίζεται ακαριαία στο Streamlit UI.
    """
    gem_client = _get_gemini_client(user_api_key)
    if not gem_client:
        yield "⚠️ Δεν βρέθηκε έγκυρο GEMINI_API_KEY στα Secrets."
        return

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

    free_models = ['gemini-2.5-flash', 'gemini-1.5-flash']
    
    for g_model in free_models:
        for attempt in range(2):
            try:
                response = gem_client.models.generate_content_stream(
                    model=g_model,
                    contents=prompt
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                return  # Επιτυχής ολοκλήρωση
            except Exception as e:
                if "503" in str(e) and attempt == 0:
                    time.sleep(1.0)
                    continue
                break
                
    yield "⚠️ Στιγμιαίος φόρτος στις υποδομές AI. Παρακαλώ δοκιμάστε ξανά."

def analyze_natal_chart_ai(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    # Fallback μη-streaming κλήσης
    full_text = ""
    for chunk in analyze_natal_chart_ai_stream(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang, user_api_key):
        full_text += chunk
    return full_text

def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    return analyze_natal_chart_ai(profile_name, transits_data, {}, "", "", "", lang, user_api_key)

def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    return analyze_natal_chart_ai(f"{p1} & {p2}", synastry_aspects, {}, "", "", "", lang, user_api_key)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    return analyze_natal_chart_ai("Chat", user_prompt, {}, "", "", "", lang, user_api_key)

def clear_ai_cache():
    pass
