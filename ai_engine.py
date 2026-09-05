# ai_engine.py
import os
import time
import streamlit as st
from google import genai
from openai import OpenAI

GEMINI_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
]

OPENROUTER_MODELS = [
    "minimax/minimax-m3:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
    "z-ai/glm-5.2:free",
    "openrouter/free",
]

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
        return OpenAI(api_key=clean_user_key, base_url="https://openrouter.ai/api/v1", timeout=45.0)

    master_key = (st.secrets.get("OPENROUTER_API_KEY", "") or os.getenv("OPENROUTER_API_KEY", "")).strip()
    if master_key:
        return OpenAI(api_key=master_key, base_url="https://openrouter.ai/api/v1", timeout=45.0)
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

    gem_client = _get_gemini_client(user_api_key)
    if gem_client:
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        for g_model in GEMINI_MODELS:
            for attempt in range(2):
                try:
                    resp = gem_client.models.generate_content(
                        model=g_model,
                        contents=full_prompt,
                    )
                    if resp and getattr(resp, "text", None):
                        return resp.text
                except Exception as e:
                    err = str(e)
                    last_errors.append(f"{g_model}: {err}")
                    if "429" in err or "RESOURCE_EXHAUSTED" in err:
                        time.sleep(4)
                        continue
                    break

    xai_key = (st.secrets.get("XAI_API_KEY", "") or os.getenv("XAI_API_KEY", "")).strip()
    if xai_key:
        try:
            xai = OpenAI(api_key=xai_key, base_url="https://api.x.ai/v1", timeout=45.0)
            response = xai.chat.completions.create(
                model="grok-4",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
        except Exception as e:
            last_errors.append(f"grok-4: {str(e)}")

    or_client = _get_openrouter_client(user_api_key)
    if or_client:
        for model_name in OPENROUTER_MODELS:
            try:
                response = or_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    extra_headers={"HTTP-Referer": "https://astrocaterpillar.streamlit.app"},
                    timeout=45.0,
                )
                if response and response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content
            except Exception as e:
                last_errors.append(f"{model_name}: {str(e)}")
                continue

    err_msg = " | ".join(last_errors) if last_errors else "Όλες οι AI μηχανές είναι εκτός σύνδεσης."
    return f"⚠️ Αδυναμία ταχείας απόκρισης AI. Παρακαλώ δοκιμάστε ξανά.\n*(Log: {err_msg})*"

def analyze_natal_chart_ai(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    lang_line = "Γράψε σε άπταιστα Ελληνικά." if lang == "el" else "Write in fluent English."
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
    4. {lang_line}
    """
    return _generate_unified_response(prompt, user_api_key)

def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    lang_line = "Απάντησε στα Ελληνικά." if lang == "el" else "Reply in English."
    prompt = f"Ανάλυση διελεύσεων για '{profile_name}' ({timeframe}): {transits_data}\n{lang_line}"
    return _generate_unified_response(prompt, user_api_key)

def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    lang_line = "Απάντησε στα Ελληνικά." if lang == "el" else "Reply in English."
    prompt = f"Ανάλυση συναστρίας {p1} & {p2}: {synastry_aspects}\n{lang_line}"
    return _generate_unified_response(prompt, user_api_key)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    lang_line = "Απάντησε στα Ελληνικά." if lang == "el" else "Reply in English."
    prompt = f"Πλαίσιο: {context_text}\nΕρώτηση: {user_prompt}\n{lang_line}"
    return _generate_unified_response(prompt, user_api_key)

def clear_ai_cache():
    pass
