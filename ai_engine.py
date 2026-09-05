# ai_engine.py - Updated API Endpoints
import os
import time
import streamlit as st
from google import genai
from openai import OpenAI

SYSTEM_PROMPT = (
    "Είσαι ένας έμπειρος, ζεστός, επικοινωνιακός και παραστατικός αστρολόγος, στο ύφος και τη φιλοσοφία της κλασικής ελληνικής αστρολογίας (όπως η Ισμήνη Καράλη και η Λίτσα Πατέρα). "
    "Ο λόγος σου είναι εκφραστικός, με συναισθηματική ροή, ενθαρρυντικός και προσιτός. "
    "ΑΠΑΓΟΡΕΥΟΝΤΑΙ οι ψυχρές λίστες με μοίρες. ΟΦΕΙΛΕΙΣ να ερμηνεύεις και να συνθέτεις τα δεδομένα."
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

    # 1. Gemini Direct (Ενημερωμένα μοντέλα 2026 + Retry για 503)
    gem_client = _get_gemini_client(user_api_key)
    if gem_client:
        active_gemini_models = ['gemini-3.6-flash', 'gemini-2.5-flash']
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        
        for g_model in active_gemini_models:
            # Δοκιμή 2 φορές σε περίπτωση προσωρινού 503 UNAVAILABLE
            for attempt in range(2):
                try:
                    resp = gem_client.models.generate_content(
                        model=g_model,
                        contents=full_prompt
                    )
                    if resp and resp.text:
                        return resp.text
                except Exception as e:
                    last_errors.append(f"Gemini ({g_model}): {str(e)}")
                    if "503" in str(e) and attempt == 0:
                        time.sleep(1.5)  # Αναμονή 1.5 δευτερόλεπτο και ξαναδοκιμή
                        continue
                    break

    # 2. OpenRouter Fallback (Ενεργά δωρεάν slugs)
    or_client = _get_openrouter_client(user_api_key)
    if or_client:
        active_or_free_models = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemini-2.5-flash:free",
            "openrouter/auto"
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
        "⚠️ Προσωρινή αυξημένη κίνηση στα AI μοντέλα.\n\n"
        "Παρακαλώ πατήστε ξανά το κουμπί υπολογισμού σε λίγα δευτερόλεπτα.\n"
        f"*(Τεχνική λεπτομέρεια: {err_msg})*"
    )

def analyze_natal_chart_ai(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    prompt = f"""
    Κάνε μια αναλυτική, ζεστή, γλαφυρή και παραστατική αστρολογική ανάλυση για το γενέθλιο προφίλ '{profile_name}', στο ύφος και τη φιλοσοφία της κλασικής ελληνικής αστρολογίας (όπως η Ισμήνη Καράλη και η Λίτσα Πατέρα).

    ΔΕΔΟΜΕΝΑ ΧΑΡΤΗ:
    - Θέσεις Πλανητών: {raw_positions}
    - Οίκοι: {houses}
    - Κινεζικό Ζώδιο: {cz_data}
    - Στοιχεία & Ποιότητες: {indicators}
    - Όψεις: {aspects}

    ΟΔΗΓΙΕΣ ΣΥΝΤΑΞΗΣ:
    1. ΜΗΝ ξεκινάς παραθέτοντας απλώς τη λίστα Ήλιου/Σελήνης/Ωροσκόπου.
    2. Ξεκίνα αμέσως την ουσιαστική ερμηνεία και σύνθεση του χάρτη.
    3. Χώρισε την ανάλυση σε:
       - **Προσωπικότητα & Συναισθηματικός Κόσμος**
       - **Έρωτας & Σχέσεις**
       - **Επαγγελματική Πορεία & Ευκαιρίες**
    4. Χρησιμοποίησε ζεστή, εκφραστική γλώσσα σε άπταιστα Ελληνικά.
    """
    return _generate_unified_response(prompt, user_api_key)

def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    prompt = f"""
    Κάνε μια ζεστή, παραστατική ανάλυση μηνιαίων διελεύσεων για το προφίλ '{profile_name}' ({timeframe}) στο ύφος της Λίτσας Πατέρα και της Ισμήνης Καράλη.
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
