# ai_engine.py - Robust Multi-Model Fallback System
import os
import time
import streamlit as st
from google import genai
from openai import OpenAI

SYSTEM_PROMPT = (
    "Είσαι ένας έμπειρος, ζεστός, επικοινωνιακός και βαθιά αφηγηματικός αστρολόγος, στο ύφος και τη φιλοσοφία της Ισμήνης Καράλη και της Λίτσας Πατέρα. "
    "Ο λόγος σου είναι γλαφυρός, συναισθηματικός και ενθαρρυντικός. "
    "ΥΠΟΧΡΕΩΤΙΚΑ ενσωματώνεις στις αναλύσεις σου στοιχεία από την ελληνική μυθολογία, την ιστορία και τα αρχαία αρχέτυπα, "
    "συνδέοντας τους πλανήτες και τις όψεις με αλληγορίες και ιστορικούς συμβολισμούς. "
    "ΑΠΑΓΟΡΕΥΟΝΤΑΙ οι ψυχρές λίστες με μοίρες. ΟΦΕΙΛΕΙΣ να ερμηνεύεις και να συνθέτεις τα δεδομένα σε μια ζωντανή αφήγηση."
)

def _get_openrouter_client(user_api_key=""):
    clean_user_key = user_api_key.strip() if user_api_key else ""
    if clean_user_key and clean_user_key.startswith("sk-or-"):
        return OpenAI(api_key=clean_user_key, base_url="https://openrouter.ai/api/v1")
    
    master_key = (
        st.secrets.get("OPENROUTER_API_KEY", "") or 
        os.getenv("OPENROUTER_API_KEY", "")
    ).strip()
    
    if master_key:
        return OpenAI(api_key=master_key, base_url="https://openrouter.ai/api/v1")
    return None

def _get_gemini_client(user_api_key=""):
    clean_user_key = user_api_key.strip() if user_api_key else ""
    if clean_user_key and not clean_user_key.startswith("sk-"):
        return genai.Client(api_key=clean_user_key)
    
    master_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "")).strip()
    if master_key:
        return genai.Client(api_key=master_key)
    return None

def _generate_unified_response(prompt: str, user_api_key: str = ""):
    last_errors = []

    # 1. Gemini Direct με Exponential Backoff & Διευρυμένα Μοντέλα
    gem_client = _get_gemini_client(user_api_key)
    if gem_client:
        active_gemini_models = [
            'gemini-3.6-flash',
            'gemini-2.5-flash',
            'gemini-2.5-pro',
            'gemini-2.0-flash'
        ]
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        
        for g_model in active_gemini_models:
            for attempt in range(3):
                try:
                    resp = gem_client.models.generate_content(
                        model=g_model,
                        contents=full_prompt
                    )
                    if resp and resp.text:
                        return resp.text
                except Exception as e:
                    err_str = str(e)
                    last_errors.append(f"Gemini ({g_model}): {err_str}")
                    if "503" in err_str or "UNAVAILABLE" in err_str:
                        time.sleep(1.0 * (attempt + 1))
                        continue
                    break

    # 2. OpenRouter Fallback με Ενεργά Free Models
    or_client = _get_openrouter_client(user_api_key)
    if or_client:
        active_or_free_models = [
            "qwen/qwen-2.5-coder-32b-instruct:free",
            "google/gemma-2-9b-it:free",
            "mistralai/mistral-7b-instruct:free"
        ]
        
        for model_name in active_or_free_models:
            try:
                response = or_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    extra_headers={
                        "HTTP-Referer": "https://astrocaterpillar.streamlit.app",
                        "X-Title": "AstroCaterpillar AI"
                    },
                    stream=False
                )
                if response and response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content
            except Exception as e:
                last_errors.append(f"OpenRouter ({model_name}): {str(e)}")
                continue

    err_msg = " | ".join(last_errors) if last_errors else "Δεν βρέθηκε διαθέσιμη AI μηχανή."
    return (
        "⚠️ Προσωρινή αυξημένη κίνηση στις υποδομές AI.\n\n"
        "Παρακαλώ δοκιμάστε ξανά σε λίγα δευτερόλεπτα.\n"
        f"*(Τεχνικό Log: {err_msg})*"
    )

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
    2. ΠΛΕΞΕ στην ανάλυση μυθολογικούς συμβολισμούς (π.χ. τους μύθους των θεών/πλανητών) και ιστορικές αλληγορίες που ταιριάζουν στις κυρίαρχες όψεις του χάρτη.
    3. Χώρισε την ανάλυση στις εξής ενότητες:
       - **Ψυχικός Πυρήνας & Αρχέτυπα (Προσωπικότητα)**
       - **Συναισθηματικά Μονοπάτια & Έρωτας**
       - **Πορεία Πεπρωμένου, Καριέρα & Ευκαιρίες**
    4. Γράψε σε άπταιστα, πλούσια Ελληνικά.
    """
    return _generate_unified_response(prompt, user_api_key)

def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    prompt = f"""
    Κάνε μια ζεστή, παραστατική ανάλυση μηνιαίων διελεύσεων για το προφίλ '{profile_name}' ({timeframe}) στο ύφος της Λίτσας Πατέρα και της Ισμήνης Καραλή.
    Δεδομένα Διελεύσεων: {transits_data}
    """
    return _generate_unified_response(prompt, user_api_key)

def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    prompt = f"""
    Κάνε μια γλαφυρή και συναισθηματική ανάλυση συναστρίας μεταξύ {p1} και {p2} στο ύφος της Ισμήνης Καράλη και της Λίτσας Πατέρα.
    Όψεις Συναστρίας: {synastry_aspects}
    """
    return _generate_unified_response(prompt, user_api_key)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    prompt = f"""
    Απάντησε στην ερώτηση του χρήστη διατηρώντας το ζεστό, εκφραστικό ύφος:
    Πλαίσιο: {context_text}
    Ερώτηση Χρήστη: {user_prompt}
    """
    return _generate_unified_response(prompt, user_api_key)

def clear_ai_cache():
    pass
