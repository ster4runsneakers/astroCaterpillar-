# ai_engine.py - AstroCaterpillar Strategic AI Module
import os
import streamlit as st

def _call_ai_provider(system_prompt: str, user_prompt: str) -> str:
    """Εσωτερική συνάρτηση κλήσης του AI παρόχου (Gemini API) με διπλό fallback."""
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return "⚠️ Δεν βρέθηκε API Key (GEMINI_API_KEY) στα secrets του Streamlit."

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{system_prompt}\n\n{user_prompt}"
        )
        return response.text
    except ImportError:
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
            return response.text
        except Exception as e:
            return f"❌ Σφάλμα κατά την επικοινωνία με το AI: {str(e)}"
    except Exception as e:
        return f"❌ Σφάλμα κατά την επικοινωνία με το AI: {str(e)}"

def analyze_natal_chart_ai(profile_name: str, positions: str, houses: str, chinese: str, stats: str, aspects: str, lang: str = "el") -> str:
    """Παράγει ψυχογραφική ανάλυση γενέθλιου χάρτη."""
    if lang == "el":
        system_prompt = (
            "Είσαι ο AstroCaterpillar, ένας αναλυτής αστρολογικής στρατηγικής. "
            "Αναλύεις γενέθλιους χάρτες με βάση δεδομένα, με ουδέτερο, κυνικό και αναλυτικό τόνο, "
            "χωρίς συναισθηματικές φορτίσεις ή υπερβολές τύπου 'Hollywood'."
        )
        user_prompt = f"""
        Προφίλ: {profile_name}
        Πλανητικές Θέσεις: {positions}
        Οίκοι: {houses}
        Κινεζικό Ζώδιο: {chinese}
        Στατιστικά Στοιχεία & Τρόποι: {stats}
        Όψεις: {aspects}
        
        Δώσε μια δομημένη ανάλυση με:
        1. **Ψυχογραφικό Προφίλ & Πυρήνας Προσωπικότητας**
        2. **Δυνατά Σημεία & Δομικές Αδυναμίες**
        3. **Στρατηγική Διαχείριση Δυναμικού**
        """
    else:
        system_prompt = (
            "You are AstroCaterpillar, a data-driven astrology strategist. "
            "Analyze natal charts objectively, with a neutral and analytical tone."
        )
        user_prompt = f"""
        Profile: {profile_name}
        Positions: {positions}
        Houses: {houses}
        Chinese Zodiac: {chinese}
        Stats: {stats}
        Aspects: {aspects}
        
        Provide a structured analysis covering Core Psychological Profile, Strengths, Weaknesses, and Strategic Guidance.
        """
    return _call_ai_provider(system_prompt, user_prompt)

def analyze_synastry_ai(p1_name: str, p2_name: str, aspects_str: str, lang: str = "el") -> str:
    """Παράγει ανάλυση συναστρίας 2 ατόμων."""
    if lang == "el":
        system_prompt = (
            "Είσαι ο AstroCaterpillar. Αναλύεις συναστρίες σχέσεων με βάση τα πραγματικά δεδομένα των όψεων, "
            "με κυνική ειλικρίνεια και εστίαση στη δυναμική αλληλεπίδρασης."
        )
        user_prompt = f"""
        Συναστρία μεταξύ: {p1_name} και {p2_name}
        Όψεις Συναστρίας: {aspects_str}
        
        Δώσε μια αναφορά με:
        1. **Σημεία Σύγκλισης & Αμοιβαίας Ενίσχυσης**
        2. **Πεδίο Τριβών & Δομικών Προκλήσεων**
        3. **Μακροπρόθεσμη Βιωσιμότητα Σχέσης**
        """
    else:
        system_prompt = (
            "You are AstroCaterpillar. Analyze synastry data objectively and analytically."
        )
        user_prompt = f"""
        Synastry between: {p1_name} and {p2_name}
        Aspects: {aspects_str}
        
        Provide analysis on Mutual Dynamics, Friction Points, and Long-Term Compatibility.
        """
    return _call_ai_provider(system_prompt, user_prompt)

def analyze_transits_ai(profile_name: str, timeframe_str: str, transits_data_str: str, lang: str = "el") -> str:
    """Παράγει στρατηγική μηνιαία ανάλυση διελεύσεων."""
    if lang == "el":
        system_prompt = (
            "Είσαι ο AstroCaterpillar, ένας αναλυτής αστρολογικής στρατηγικής. "
            "Αναλύεις τις μηνιαίες διελεύσεις με βάση τα πραγματικά δεδομένα, χωρίς μελοδραματισμούς, "
            "με ουδέτερο και αναλυτικό τόνο. "
            "Διαχώρισε τις μακροπρόθεσμες τάσεις (αργοί πλανήτες) από τους ημερήσιους πυροκροτητές (γρήγοροι πλανήτες)."
        )
        user_prompt = f"""
        Προφίλ: {profile_name}
        Περίοδος Ανάλυσης: {timeframe_str}
        
        Δεδομένα Διελεύσεων (Όψεις):
        {transits_data_str}
        
        Δώσε μια δομημένη μηνιαία αναφορά με την εξής δομή:
        1. **Κυρίαρχο Μακρο-Πλαίσιο (Macro Trends):** Οι επιδράσεις των αργών πλανητών (Δίας, Κρόνος, Ουρανός, Ποσειδώνας, Πλούτωνας). Τι τομείς πιέζουν ή ξεκλειδώνουν.
        2. **Πυροκροτητές & Κρίσιμες Ημέρες (Triggers):** Πότε οι γρήγοροι πλανήτες ενεργοποιούν τα μακρο-σενάρια μέσα στον μήνα.
        3. **Τακτική Διαχείριση (Strategic Action):** Συγκεκριμένες, ψύχραιμες οδηγίες για τη βέλτιστη διαχείριση ρίσκου και ευκαιριών.
        """
    else:
        system_prompt = (
            "You are AstroCaterpillar, an astrological strategy analyst. "
            "Analyze monthly transits neutrally and objectively. "
            "Separate macro-level planetary cycles from short-term triggers."
        )
        user_prompt = f"""
        Profile: {profile_name}
        Timeframe: {timeframe_str}
        
        Transit Data (Aspects):
        {transits_data_str}
        
        Provide a structured monthly report:
        1. **Macro Framework (Outer Planets):** Structural shifts and high-impact cycles.
        2. **Triggers & Key Dates:** How inner planets activate the macro trends.
        3. **Strategic Action:** Data-driven advice for risk management and opportunity.
        """
    return _call_ai_provider(system_prompt, user_prompt)

def ask_caterpillar_chat(report_context: str, question: str, lang: str = "el") -> str:
    """Απαντά σε ερωτήσεις χρήστη πάνω σε παραχθείσα ανάλυση."""
    system_prompt = "Είσαι ο AstroCaterpillar. Απάντησε σύντομα, με ακρίβεια και βάση τα δεδομένα της ανάλυσης."
    user_prompt = f"Πλαίσιο Ανάλυσης:\n{report_context}\n\nΕρώτηση Χρήστη: {question}"
    return _call_ai_provider(system_prompt, user_prompt)

def clear_ai_cache():
    """Καθαρίζει τα αποθηκευμένα αποτελέσματα AI από το session state."""
    keys_to_del = [k for k in st.session_state.keys() if k.startswith("natal_ai_")]
    for k in keys_to_del:
        del st.session_state[k]
