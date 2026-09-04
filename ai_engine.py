# ai_engine.py - AstroCaterpillar AI Engine (Hybrid BYOK & Verified Stable Fallback)
import os
import streamlit as st
from google import genai

# Λίστα ενεργών & σταθερών μοντέλων
PRIMARY_MODEL = 'gemini-2.5-flash'
FALLBACK_MODELS = ['gemini-2.5-flash-lite', 'gemini-1.5-flash']

def _get_client(user_api_key=""):
    """
    Προτεραιότητα 1: Το API Key που πληκτρολόγησε ο χρήστης στη Sidebar.
    Προτεραιότητα 2: Το Master Key από τα Secrets (ΜΟΝΟ αν ο χρήστης είναι Admin).
    """
    clean_user_key = user_api_key.strip() if user_api_key else ""
    
    if clean_user_key:
        return genai.Client(api_key=clean_user_key), None
    
    # Αν δεν έδωσε Key ο χρήστης, ελέγχουμε αν είναι Admin
    is_admin = st.session_state.get("is_admin", False)
    master_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    
    if is_admin and master_key:
        return genai.Client(api_key=master_key), None
    
    if not clean_user_key and not is_admin:
        return None, "🔑 Παρακαλώ εισάγετε το δικό σας Gemini API Key στη Sidebar για να χρησιμοποιήσετε τις AI λειτουργίες."
    
    return None, "⚠️ Δεν βρέθηκε έγκυρο API Key."

def _generate_with_fallback(client, prompt):
    """
    Δοκιμάζει το Primary Model (gemini-2.5-flash).
    Αν εξαντληθεί το Quota (429) ή βρει σφάλμα, περνάει αυτόματα στα διαθέσιμα Fallback μοντέλα.
    """
    models_to_try = [PRIMARY_MODEL] + FALLBACK_MODELS
    last_error = ""
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            last_error = str(e)
            # Αν είναι σφάλμα ορίου (429/RESOURCE_EXHAUSTED) ή 404, δοκιμάζουμε το επόμενο μοντέλο
            if any(err_code in last_error for err_code in ["429", "RESOURCE_EXHAUSTED", "404", "NOT_FOUND"]):
                continue
            else:
                break

    return (
        "⚠️ Το ημερήσιο όριο αιτημάτων (Quota) εξαντλήθηκε στο τρέχον API Key.\n\n"
        "**Τι μπορείτε να κάνετε:**\n"
        "1. Εισάγετε ένα δικό σας δωρεάν API Key στη Sidebar από το [Google AI Studio](https://aistudio.google.com/).\n"
        "2. Αν είστε Admin, περιμένετε λίγα λεπτά να μηδενιστεί ο μετρητής της Google."
    )

def analyze_natal_chart_ai(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el", user_api_key=""):
    client, err = _get_client(user_api_key)
    if err:
        return err

    system_prompt = (
        "Είσαι ο Caterpillar – ένας αναλυτής αστρολογίας που λειτουργεί ως peer, μιλάει με την αλήθεια των αριθμών και των γεγονότων. "
        "Οι αναλύσεις σου είναι αποκλειστικά βασισμένες σε δεδομένα, με ουδέτερο τόνο, χωρίς υπερβολές ή συναισθηματικές φορτίσεις και χωρίς επαναλήψεις."
    )
    
    prompt = f"""
    {system_prompt}
    
    Ανάλυσε το γενέθλιο προφίλ '{profile_name}' με βάση τα παρακάτω δεδομένα:
    - Θέσεις Πλανητών: {raw_positions}
    - Οίκοι: {houses}
    - Κινεζικό Ζώδιο: {cz_data}
    - Στοιχεία & Ποιότητες: {indicators}
    - Όψεις: {aspects}
    
    Γλώσσα απάντησης: {'Ελληνικά' if lang == 'el' else 'English'}.
    """
    
    return _generate_with_fallback(client, prompt)

def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el", user_api_key=""):
    client, err = _get_client(user_api_key)
    if err:
        return err

    prompt = f"""
    Είσαι ο Caterpillar. Κάνε μια αναλυτική, δεδομενοκεντρική στρατηγική ανάλυση μηνιαίων διελεύσεων για το προφίλ '{profile_name}' ({timeframe}):
    Δεδομένα Διελεύσεων: {transits_data}
    
    Γλώσσα απάντησης: {'Ελληνικά' if lang == 'el' else 'English'}.
    """
    
    return _generate_with_fallback(client, prompt)

def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el", user_api_key=""):
    client, err = _get_client(user_api_key)
    if err:
        return err

    prompt = f"""
    Είσαι ο Caterpillar. Κάνε μια ουδέτερη και διαισθητική ανάλυση συναστρίας μεταξύ {p1} και {p2}:
    Όψεις Συναστρίας: {synastry_aspects}
    
    Γλώσσα απάντησης: {'Ελληνικά' if lang == 'el' else 'English'}.
    """
    
    return _generate_with_fallback(client, prompt)

def ask_caterpillar_chat(context_text, user_prompt, lang="el", user_api_key=""):
    client, err = _get_client(user_api_key)
    if err:
        return err

    full_query = f"""
    Είσαι ο Caterpillar. Απάντησε στην ερώτηση του χρήστη με βάση το παρακάτω πλαίσιο και ιστορικό, διατηρώντας ουδέτερο και δεδομενοκεντρικό ύφος.
    
    Πλαίσιο / Ιστορικό:
    {context_text}
    
    Ερώτηση Χρήστη:
    {user_prompt}
    """
    
    return _generate_with_fallback(client, full_query)

def clear_ai_cache():
    pass
