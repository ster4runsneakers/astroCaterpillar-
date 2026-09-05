# ai_engine.py - Direct & Fast Execution
import os
import streamlit as st
from openai import OpenAI

SYSTEM_PROMPT = (
    "Είσαι ένας έμπειρος, ζεστός, επικοινωνιακός και βαθιά αφηγηματικός αστρολόγος, στο ύφος της Ισμήνης Καράλη και της Λίτσας Πατέρα. "
    "Ο λόγος σου είναι γλαφυρός, συναισθηματικός και ενθαρρυντικός. "
    "ΥΠΟΧΡΕΩΤΙΚΑ ενσωματώνεις στις αναλύσεις σου στοιχεία από την ελληνική μυθολογία, την ιστορία και τα αρχαία αρχέτυπα, "
    "συνδέοντας τους πλανήτες και τις όψεις με αλληγορίες. "
    "ΑΠΑΓΟΡΕΥΟΝΤΑΙ οι ψυχρές λίστες με μοίρες. ΟΦΕΙΛΕΙΣ να ερμηνεύεις και να συνθέτεις τα δεδομένα."
)

def _get_openrouter_client(user_api_key=""):
    clean_user_key = user_api_key.strip() if user_api_key else ""
    if clean_user_key and clean_user_key.startswith("sk-or-"):
        return OpenAI(api_key=clean_user_key, base_url="https://openrouter.ai/api/v1", timeout=12.0)
    
    master_key = (st.secrets.get("OPENROUTER_API_KEY", "") or os.getenv("OPENROUTER_API_KEY", "")).strip()
    if master_key:
        return OpenAI(api_key=master_key, base_url="https://openrouter.ai/api/v1", timeout=12.0)
    return None

def _generate_unified_response(prompt: str, user_api_key: str = ""):
    # Χρήση OpenRouter με επιβεβαιωμένα ενεργά μοντέλα για να αποφευχθούν τα deadlocks του Gemini SDK
    or_client = _get_openrouter_client(user_api_key)
    
    if or_client:
        # Δοκιμάζουμε απευθείας τα πιο γρήγορα και σταθερά μοντέλα
        working_models = [
            "google/gemini-2.0-flash-001",
            "meta-llama/llama-3.3-70b-instruct",
            "deepseek/deepseek-chat",
            "openrouter/auto"
        ]
        
        for model_name in working_models:
            try:
                response = or_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    extra_headers={"HTTP-Referer": "https://astrocaterpillar.streamlit.app"},
                    timeout=10.0
                )
                if response and response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content
            except Exception:
                continue

    return "⚠️ Η μηχανή AI είναι προσωρινά απασχολημένη. Παρακαλώ κάντε ξανά κλικ στο κουμπί υπολογισμού."

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
