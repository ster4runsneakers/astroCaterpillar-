# ai_engine.py - AstroCaterpillar AI Engine (With Updated Active Model Fallback)
import os
import streamlit as st
from google import genai

# Ενεργά μοντέλα SDK
PRIMARY_MODEL = 'gemini-2.5-flash'
FALLBACK_MODEL = 'gemini-2.5-flash-lite'

def _get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def _generate_with_fallback(client, prompt):
    """
    Δοκιμάζει πρώτα το Primary Model (2.5-flash). 
    Αν αποτύχει λόγω Quota (429), περνάει αυτόματα στο Fallback Model (2.5-flash-lite).
    """
    try:
        # 1η Προσπάθεια: Gemini 2.5 Flash
        response = client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        err_str = str(e)
        # Αν το σφάλμα αφορά όριο αιτημάτων (429 / Resource Exhausted)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            try:
                # 2η Προσπάθεια: Μετάβαση στο Gemini 2.5 Flash Lite
                response = client.models.generate_content(
                    model=FALLBACK_MODEL,
                    contents=prompt,
                )
                return response.text
            except Exception as fallback_err:
                return "⚠️ Το ημερήσιο όριο εξαντλήθηκε προσωρινά. Παρακαλώ δοκιμάστε ξανά σε λίγα λεπτά."
        else:
            return f"⚠️ Σφάλμα κατά την παραγωγή της ανάλυσης: {err_str}"

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
