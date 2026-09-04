# ai_engine.py - AstroCaterpillar Stable Engine (Robust Quota & Free OpenRouter Slugs)
import os
import streamlit as st
from google import genai
from openai import OpenAI

SYSTEM_PROMPT = (
    "Είσαι ο Caterpillar – ένας αναλυτής αστρολογίας που λειτουργεί ως peer, μιλάει με την αλήθεια των αριθμών και των γεγονότων. "
    "Ο τόνος σου είναι αυστηρά επαγγελματικός, αναλυτικός, δεδομενοκεντρικός και ουδέτερος. "
    "ΑΠΑΓΟΡΕΥΟΝΤΑΙ οι παραμορφωμένες λέξεις, τα αγγλικά terms ανακατεμένα με ελληνικά και η απλή επανάληψη των μοιρών. "
    "ΟΦΕΙΛΕΙΣ να συνθέτεις τα δεδομένα σε στρατηγικά συμπεράσματα. "
    "Χρησιμοποίησε άπταιστα Ελληνικά με τη σωστή αστρολογική ορολογία."
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

    # 1. Gemini Direct (Δοκιμή σε πολλαπλά μοντέλα με ανεξάρτητα Quotas)
    gem_client = _get_gemini_client(user_api_key)
    if gem_client:
        # Δοκιμάζουμε 3 διαφορετικά μοντέλα της Google - αν το 2.5 φτάσει όριο, περνάει στο 2.0
        gemini_models = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        
        for g_model in gemini_models:
            try:
                resp = gem_client.models.generate_content(
                    model=g_model,
                    contents=full_prompt
                )
                if resp and resp.text:
                    return resp.text
            except Exception as e:
                last_errors.append(f"Gemini ({g_model}): {str(e)}")
                continue

    # 2. OpenRouter (Μόνο ΕΝΕΡΓΑ ΔΩΡΕΑΝ slugs που ΔΕΝ απαιτούν credits)
    or_client = _get_openrouter_client(user_api_key)
    if or_client:
        verified_free_models = [
            "google/gemini-2.0-flash-lite-preview-02-05:free",
            "google/gemini-2.0-pro-exp-02-05:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "openrouter/free"
        ]
        
        for model_name in verified_free_models:
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
        "⚠️ Εξαντλήθηκαν προσωρινά τα ημερήσια όρια αιτημάτων.\n\n"
        "**Γρήγορη Λύση:** Εισάγετε ένα δικό σας δωρεάν Gemini API Key στη Sidebar από το [Google AI Studio](https://aistudio.google.com/).\n\n"
        f"*(Τεχνική λεπτομέρεια: {err_msg})*"
    )

def analyze_natal_chart_ai(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    prompt = f"""
    Κάνε μια ολοκληρωμένη, σοβαρή και στρατηγική αστρολογική ανάλυση για το γενέθλιο προφίλ '{profile_name}'.

    ΔΕΔΟΜΕΝΑ:
    - Θέσεις Πλανητών: {raw_positions}
    - Οίκοι: {houses}
    - Κινεζικό Ζώδιο: {cz_data}
    - Κατανομή Στοιχείων & Ποιοτήτων: {indicators}
    - Κύριες Όψεις: {aspects}

    ΟΔΗΓΙΕΣ ΣΥΝΤΑΞΗΣ:
    1. ΜΗΝ επαναλάβεις απλά τους αριθμούς και τις μοίρες.
    2. Αναλυσε τη δομή της προσωπικότητας, τα δυνατά σημεία και τις εσωτερικές συγκρούσεις.
    3. Δώσε έμφαση στη στρατηγική κατεύθυνση, την καριέρα (10ος οίκος) και τη διαχείριση πόρων.
    4. Γράψε σε άπταιστα Ελληνικά με σωστή ορολογία.
    """
    return _generate_unified_response(prompt, user_api_key)

def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    prompt = f"""
    Κάνε μια στρατηγική ανάλυση μηνιαίων διελεύσεων για το προφίλ '{profile_name}' ({timeframe}):
    Δεδομένα Διελεύσεων: {transits_data}
    
    Εστίασε στους μακρο-κύκλους, στις ευκαιρίες και στους κινδύνους του μήνα με καθαρό, δεδομενοκεντρικό λόγο.
    """
    return _generate_unified_response(prompt, user_api_key)

def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    prompt = f"""
    Κάνε μια ουδέτερη, διαισθητική και στρατηγική ανάλυση συναστρίας μεταξύ {p1} και {p2}:
    Όψεις Συναστρίας: {synastry_aspects}
    
    Εστίασε στη δυναμική της σχέσης, στα σημεία τριβής και στα πεδία συνεργασίας.
    """
    return _generate_unified_response(prompt, user_api_key)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    prompt = f"""
    Απάντησε στην ερώτηση του χρήστη με βάση το παρακάτω πλαίσιο, διατηρώντας το σοβαρό και δεδομενοκεντρικό ύφος του Caterpillar:
    
    Πλαίσιο:
    {context_text}
    
    Ερώτηση Χρήστη:
    {user_prompt}
    """
    return _generate_unified_response(prompt, user_api_key)

def clear_ai_cache():
    pass
