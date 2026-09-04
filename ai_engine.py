# ai_engine.py - AstroCaterpillar Unified Engine (Updated Active Free Slugs & Gemini 2.5)
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

    # 1η Προσπάθεια: OpenRouter με ΕΝΕΡΓΑ ΔΩΡΕΑΝ ΜΟΝΤΕΛΑ
    or_client = _get_openrouter_client(user_api_key)
    if or_client:
        active_free_or_models = [
            "google/gemini-2.5-flash:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "mistralai/mistral-7b-instruct:free"
        ]
        
        for or_model in active_free_or_models:
            try:
                response = or_client.chat.completions.create(
                    model=or_model,
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
                last_errors.append(f"OpenRouter ({or_model}): {str(e)}")
                continue

    # 2η Προσπάθεια: Gemini SDK Direct (gemini-2.5-flash)
    gem_client = _get_gemini_client(user_api_key)
    if gem_client:
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        try:
            resp = gem_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt
            )
            if resp and resp.text:
                return resp.text
        except Exception as e:
            last_errors.append(f"Gemini (gemini-2.5-flash): {str(e)}")

    # Αν αποτύχουν όλα
    err_msg = " | ".join(last_errors) if last_errors else "Δεν βρέθηκαν έγκυρα API Keys."
    return (
        "⚠️ Εξαντλήθηκαν προσωρινά τα ημερήσια όρια αιτημάτων.\n\n"
        "**Λύσεις:**\n"
        "1. Εισάγετε ένα δικό σας Gemini API Key στη Sidebar από το [Google AI Studio](https://aistudio.google.com/).\n"
        "2. Περιμένετε 30 δευτερόλεπτα και δοκιμάστε ξανά.\n\n"
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
