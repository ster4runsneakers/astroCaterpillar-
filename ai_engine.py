# ai_engine.py - AstroCaterpillar AI Engine (Updated Model Names & Robust Fallback)
import os
import streamlit as st
from google import genai

# Λίστα ενεργών μοντέλων για το google-genai SDK
PRIMARY_MODEL = 'gemini-2.5-flash'
FALLBACK_MODELS = ['gemini-1.5-flash', 'gemini-2.5-pro']

def _get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def _generate_with_fallback(client, prompt):
    """
    Δοκιμάζει το Primary Model. Αν αποτύχει λόγω Quota/Rate Limit (429) ή 404,
    μεταβαίνει αυτόματα στα διαθέσιμα Fallback μοντέλα.
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
        "⚠️ Το ημερήσιο όριο (Quota) εξαντλήθηκε στο τρέχον API Key.\n\n"
        "**Λύσεις:**\n"
        "1. Περίμενε να μηδενιστεί ο ημερήσιος μετρητής της Google.\n"
        "2. Δημιούργησε ένα νέο δωρεάν API Key από το [Google AI Studio](https://aistudio.google.com/) "
        "και αντικατάστησέ το στα Streamlit Secrets (`GEMINI_API_KEY`)."
    )

def analyze_natal_chart_ai(profile_name, raw_positions, houses, cz_data, indicators, aspects, lang="el"):
    client = _get_client()
    if not client:
        return "⚠️ Σφάλμα: Δεν βρέθηκε το `GEMINI_API_KEY` στα Streamlit Secrets."

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

def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el"):
    client = _get_client()
    if not client:
        return "⚠️ Σφάλμα: Δεν βρέθηκε το `GEMINI_API_KEY`."

    prompt = f"""
    Είσαι ο Caterpillar. Κάνε μια αναλυτική, δεδομενοκεντρική στρατηγική ανάλυση μηνιαίων διελεύσεων για το προφίλ '{profile_name}' ({timeframe}):
    Δεδομένα Διελεύσεων: {transits_data}
    
    Γλώσσα απάντησης: {'Ελληνικά' if lang == 'el' else 'English'}.
    """
    
    return _generate_with_fallback(client, prompt)

def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el"):
    client = _get_client()
    if not client:
        return "⚠️ Σφάλμα: Δεν βρέθηκε το `GEMINI_API_KEY`."

    prompt = f"""
    Είσαι ο Caterpillar. Κάνε μια ουδέτερη και διαισθητική ανάλυση συναστρίας μεταξύ {p1} και {p2}:
    Όψεις Συναστρίας: {synastry_aspects}
    
    Γλώσσα απάντησης: {'Ελληνικά' if lang == 'el' else 'English'}.
    """
    
    return _generate_with_fallback(client, prompt)

def ask_caterpillar_chat(context_text, user_prompt, lang="el"):
    client = _get_client()
    if not client:
        return "⚠️ Σφάλμα: Δεν βρέθηκε το `GEMINI_API_KEY`."

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
