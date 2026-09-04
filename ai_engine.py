# ai_engine.py - AstroCaterpillar Unified Engine (OpenRouter + Gemini Fallback)
import os
import streamlit as st
from google import genai
from openai import OpenAI

SYSTEM_PROMPT = (
    "Είσαι ο Caterpillar – ένας αναλυτής αστρολογίας που λειτουργεί ως peer, μιλάει με την αλήθεια των αριθμών και των γεγονότων. "
    "Οι αναλύσεις σου είναι αποκλειστικά βασισμένες σε δεδομένα, με ουδέτερο τόνο, χωρίς υπερβολές ή συναισθηματικές φορτίσεις και χωρίς επαναλήψεις."
)

def _get_openrouter_client(user_api_key=""):
    clean_user_key = user_api_key.strip() if user_api_key else ""
    if clean_user_key and clean_user_key.startswith("sk-or-"):
        return OpenAI(api_key=clean_user_key, base_url="https://openrouter.ai/api/v1")
    
    # Έλεγχος στα Secrets για OPENROUTER_API_KEY ή DEEPSEEK_API_KEY
    master_key = (
        st.secrets.get("OPENROUTER_API_KEY", "") or 
        st.secrets.get("DEEPSEEK_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
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

    # 1η Προσπάθεια: OpenRouter (DeepSeek V3)
    or_client = _get_openrouter_client(user_api_key)
    if or_client:
        try:
            response = or_client.chat.completions.create(
                model="deepseek/deepseek-chat",
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
            if response and response.choices:
                return response.choices[0].message.content
        except Exception as e:
            last_errors.append(f"OpenRouter/DeepSeek: {str(e)}")

    # 2η Προσπάθεια: Gemini Fallback
    gem_client = _get_gemini_client(user_api_key)
    if gem_client:
        models_to_try = ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-1.5-flash']
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        for m_name in models_to_try:
            try:
                resp = gem_client.models.generate_content(model=m_name, contents=full_prompt)
                if resp and resp.text:
                    return resp.text
            except Exception as e:
                last_errors.append(f"{m_name}: {str(e)}")
                continue

    # Αν αποτύχουν όλα
    err_msg = " | ".join(last_errors) if last_errors else "Δεν βρέθηκαν έγκυρα API Keys."
    return (
        "⚠️ Το ημερήσιο όριο αιτημάτων (Quota) εξαντλήθηκε ή δεν βρέθηκε ενεργό API Key.\n\n"
        "**Τι μπορείτε να κάνετε:**\n"
        "1. Βεβαιωθείτε ότι το `OPENROUTER_API_KEY` (ή `DEEPSEEK_API_KEY`) έχει προστεθεί στα Streamlit Secrets.\n"
        "2. Εισάγετε ένα δικό σας API Key στη Sidebar.\n\n"
        f"*(Τεχνική λεπτομέρεια: {err_msg})*"
    )

def analyze_natal_chart_ai(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    prompt = f"""
    Ανάλυσε το γενέθλιο προφίλ '{profile_name}' με βάση τα παρακάτω δεδομένα:
    - Θέσεις Πλανητών: {raw_positions}
    - Οίκοι: {houses}
    - Κινεζικό Ζώδιο: {cz_data}
    - Στοιχεία & Ποιότητες: {indicators}
    - Όψεις: {aspects}
    
    Γλώσσα απάντησης: {'Ελληνικά' if lang == 'el' else 'English'}.
    """
    return _generate_unified_response(prompt, user_api_key)

def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    prompt = f"""
    Κάνε μια αναλυτική, δεδομενοκεντρική στρατηγική ανάλυση μηνιαίων διελεύσεων για το προφίλ '{profile_name}' ({timeframe}):
    Δεδομένα Διελεύσεων: {transits_data}
    
    Γλώσσα απάντησης: {'Ελληνικά' if lang == 'el' else 'English'}.
    """
    return _generate_unified_response(prompt, user_api_key)

def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    prompt = f"""
    Κάνε μια ουδέτερη και διαισθητική ανάλυση συναστρίας μεταξύ {p1} και {p2}:
    Όψεις Συναστρίας: {synastry_aspects}
    
    Γλώσσα απάντησης: {'Ελληνικά' if lang == 'el' else 'English'}.
    """
    return _generate_unified_response(prompt, user_api_key)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    prompt = f"""
    Απάντησε στην ερώτηση του χρήστη με βάση το παρακάτω πλαίσιο και ιστορικό:
    
    Πλαίσιο / Ιστορικό:
    {context_text}
    
    Ερώτηση Χρήστη:
    {user_prompt}
    """
    return _generate_unified_response(prompt, user_api_key)

def clear_ai_cache():
    pass
