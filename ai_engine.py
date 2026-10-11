# ai_engine.py
import hashlib
import os
import time
import streamlit as st
from google import genai
from google.genai import types as genai_types
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


_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ai_cache")
_FRESH = False  # όταν True, αγνοεί την αποθηκευμένη ανάλυση και γράφει νέα


def set_fresh(flag: bool):
    global _FRESH
    _FRESH = bool(flag)


def _cache_path(prompt: str):
    h = hashlib.sha256((SYSTEM_PROMPT + "\n" + prompt).encode("utf-8")).hexdigest()
    return os.path.join(_CACHE_DIR, h + ".txt")


def _cache_get(prompt: str):
    if _FRESH:
        return None
    try:
        with open(_cache_path(prompt), "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _cache_put(prompt: str, text: str):
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        with open(_cache_path(prompt), "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        pass


def _secret(name: str) -> str:
    """Safe secret lookup: never crashes when secrets.toml is missing."""
    try:
        val = st.secrets.get(name, "")
    except Exception:
        val = ""
    return str(val or os.getenv(name, "") or "").strip()

def _get_openrouter_client(user_api_key=""):
    clean_user_key = user_api_key.strip() if user_api_key else ""
    if clean_user_key and clean_user_key.startswith("sk-or-"):
        return OpenAI(api_key=clean_user_key, base_url="https://openrouter.ai/api/v1", timeout=45.0)

    master_key = _secret("OPENROUTER_API_KEY")
    if master_key:
        return OpenAI(api_key=master_key, base_url="https://openrouter.ai/api/v1", timeout=45.0)
    return None

def _get_gemini_client(user_api_key=""):
    clean_user_key = user_api_key.strip() if user_api_key else ""
    if clean_user_key and not clean_user_key.startswith("sk-"):
        return genai.Client(api_key=clean_user_key)
    
    master_key = _secret("GEMINI_API_KEY")
    if master_key:
        return genai.Client(api_key=master_key)
    return None

def _generate_unified_response(prompt: str, user_api_key: str = "", use_cache: bool = False):
    if use_cache:
        cached = _cache_get(prompt)
        if cached:
            return cached
    result = _generate_raw(prompt, user_api_key)
    if use_cache and result and not str(result).startswith("⚠️"):
        _cache_put(prompt, result)
    return result


def _generate_raw(prompt: str, user_api_key: str = ""):
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
                        config=genai_types.GenerateContentConfig(temperature=0.0, seed=42),
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

    xai_key = _secret("XAI_API_KEY")
    if xai_key:
        try:
            xai = OpenAI(api_key=xai_key, base_url="https://api.x.ai/v1", timeout=45.0)
            response = xai.chat.completions.create(
                model="grok-4",
                temperature=0,
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
                    temperature=0,
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
    return _generate_unified_response(prompt, user_api_key, use_cache=True)

def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    lang_line = "Απάντησε στα Ελληνικά." if lang == "el" else "Reply in English."
    prompt = f"Ανάλυση διελεύσεων για '{profile_name}' ({timeframe}): {transits_data}\n{lang_line}"
    return _generate_unified_response(prompt, user_api_key, use_cache=True)

def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    lang_line = "Απάντησε στα Ελληνικά." if lang == "el" else "Reply in English."
    prompt = f"Ανάλυση συναστρίας {p1} & {p2}: {synastry_aspects}\n{lang_line}"
    return _generate_unified_response(prompt, user_api_key, use_cache=True)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    lang_line = "Απάντησε στα Ελληνικά." if lang == "el" else "Reply in English."
    prompt = f"Πλαίσιο: {context_text}\nΕρώτηση: {user_prompt}\n{lang_line}"
    return _generate_unified_response(prompt, user_api_key)

def clear_ai_cache():
    pass
