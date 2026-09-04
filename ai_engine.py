# ai_engine.py - AstroCaterpillar AI Integration Engine (using official google-genai SDK)
import os
import streamlit as st
from google import genai

def _get_client():
    # Ανάκτηση του API Key από Streamlit Secrets ή Environment Variables
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

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
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ Σφάλμα κατά την παραγωγή της ανάλυσης: {str(e)}"

def analyze_transits_ai(profile_name, timeframe, transits_data, lang="el"):
    client = _get_client()
    if not client:
        return "⚠️ Σφάλμα: Δεν βρέθηκε το `GEMINI_API_KEY`."

    prompt = f"""
    Είσαι ο Caterpillar. Κάνε μια αναλυτική, δεδομενοκεντρική στρατηγική ανάλυση μηνιαίων διελεύσεων για το προφίλ '{profile_name}' ({timeframe}):
    Δεδομένα Διελεύσεων: {transits_data}
    
    Γλώσσα απάντησης: {'Ελληνικά' if lang == 'el' else 'English'}.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ Σφάλμα κατά την παραγωγή της ανάλυσης: {str(e)}"

def analyze_synastry_ai(p1, p2, synastry_aspects, lang="el"):
    client = _get_client()
    if not client:
        return "⚠️ Σφάλμα: Δεν βρέθηκε το `GEMINI_API_KEY`."

    prompt = f"""
    Είσαι ο Caterpillar. Κάνε μια ουδέτερη και διαισθητική ανάλυση συναστρίας μεταξύ {p1} και {p2}:
    Όψεις Συναστρίας: {synastry_aspects}
    
    Γλώσσα απάντησης: {'Ελληνικά' if lang == 'el' else 'English'}.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ Σφάλμα κατά την παραγωγή της ανάλυσης: {str(e)}"

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
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_query,
        )
        return response.text
    except Exception as e:
        return f"⚠️ Σφάλμα κατά τη συνομιλία: {str(e)}"

def clear_ai_cache():
    pass
