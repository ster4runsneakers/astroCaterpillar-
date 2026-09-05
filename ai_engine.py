# ai_engine.py - Real-Time Streaming Engine
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

def analyze_natal_chart_ai_stream(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    """
    Generator που στέλνει ακαριαία τα chunks στο Streamlit st.write_stream
    """
    if not _configure_gemini(user_api_key):
        yield "⚠️ Δεν βρέθηκε έγκυρο GEMINI_API_KEY."
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

    # Δοκιμή σταθερών μοντέλων Flash
    active_models = ['gemini-2.5-flash', 'gemini-1.5-flash']
    
    for model_name in active_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt, stream=True)
            
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
            return  # Ολοκληρώθηκε με επιτυχία
            
        except Exception as e:
            err_str = str(e)
            if "503" in err_str:
                time.sleep(1.0)
                continue
            continue

    yield "⚠️ Προσωρινός φόρτος στις υποδομές της Google. Παρακαλώ ξαναδοκιμάστε σε λίγα δευτερόλεπτα."

def analyze_natal_chart_ai(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
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
