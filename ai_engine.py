# ai_engine.py - AstroCaterpillar Rich Astrological Persona Engine (Dual SDK Support)
import os

SYSTEM_PERSONA = """
Είσαι ο AstroCaterpillar, ένας έμπειρος, διεισδυτικός και γλαφυρός αστρολόγος.
Το ύφος σου συνδυάζει τη βαθιά ψυχολογική και μυθολογική ανάλυση της Ισμήνης Καράλη με την παραστατική, ζεστή και άμεσα εφαρμόσιμη αστρολογική σοφία της Λίτσα Πατέρα.

Κανόνες Γραφής:
1. Μη δίνεις στεγνούς ορισμούς ή ρομποτικές λίστες.
2. Συνέθεσε τα στοιχεία (Ζώδια, Οίκους, Όψεις, Στοιχεία) σε μια ρέουσα, ατμοσφαιρική αφήγηση.
3. Εστίασε στην εσωτερική ψυχολογία, τα κρυφά χαρίσματα, τα διλήμματα της ψυχής και τις καρμικές προκλήσεις.
4. Χρησιμοποίησε πλούσιο λεξιλόγιο, μεταφορές και ζωντανά παραδείγματα.
5. Διατήρησε την απάντηση στην αιτούμενη γλώσσα (Ελληνικά ή Αγγλικά).
"""

def generate_ai_text(prompt: str) -> str:
    """Εκτελεί το API call χρησιμοποιώντας είτε το νέο google-genai είτε το παλιό google-generativeai."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Το GEMINI_API_KEY δεν βρέθηκε στις ρυθμίσεις του Streamlit Cloud (Secrets)."

    # 1. Δοκιμή με το νέο SDK: google-genai
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception:
        pass

    # 2. Fallback στο παλιό SDK: google-generativeai
    try:
        import google.generativeai as genai_old
        genai_old.configure(api_key=api_key)
        model = genai_old.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Σφάλμα κατά την παραγωγή της ανάλυσης: {str(e)}"


def analyze_natal_chart_ai(name, positions, houses, chinese_data, elements, aspects, lang="el"):
    prompt = f"""
    {SYSTEM_PERSONA}
    
    Γλώσσα Απάντησης: {"Ελληνικά" if lang == "el" else "English"}
    
    Προφίλ: {name}
    - Πλανητικές Θέσεις: {positions}
    - Αιχμές Οίκων: {houses}
    - Κινεζικό Ζώδιο & Στοιχείο: {chinese_data}
    - Κατανομή Στοιχείων & Πιοτήτων: {elements}
    - Γενέθλιες Όψεις: {aspects}
    
    Παρακαλώ στείλε μια πλήρη, γλαφυρή και βαθιά ψυχολογική/αστρολογική ανάλυση του χάρτη.
    Ανάλυσε τον πυρήνα της προσωπικότητας (Ήλιος, Σελήνη, Ωροσκόπος/1ος Οίκος), τις συναισθηματικές ανάγκες, τα ταλέντα, τις εσωτερικές συγκρούσεις (όψεις) και τη συνδυαστική σοφία του Κινεζικού Ζωδίου.
    """
    return generate_ai_text(prompt)


def analyze_transits_ai(name, timeframe, transits_data, lang="el"):
    prompt = f"""
    {SYSTEM_PERSONA}
    
    Γλώσσα Απάντησης: {"Ελληνικά" if lang == "el" else "English"}
    
    Προφίλ: {name}
    Χρονική Περίοδος: {timeframe}
    Δεδομένα Διελεύσεων: {transits_data}
    
    Κάνε μια ζωντανή, προγνωστική και συμβουλευτική ανάλυση για τον μήνα αυτό.
    Ξεχώρισε τις μεγάλες, κοσμικές τάσεις των αργών πλανητών (μακρο-κύκλοι) και πώς επηρεάζουν την ψυχολογία, τα επαγγελματικά και τις σχέσεις του ατόμου.
    """
    return generate_ai_text(prompt)


def analyze_synastry_ai(p1_name, p2_name, aspects_data, lang="el"):
    prompt = f"""
    {SYSTEM_PERSONA}
    
    Γλώσσα Απάντησης: {"Ελληνικά" if lang == "el" else "English"}
    
    Συναστρία μεταξύ {p1_name} και {p2_name}
    Όψεις Συναστρίας: {aspects_data}
    
    Ανάλυσε τη χημεία, την ερωτική/συναισθηματική έλξη, τα σημεία τριβής και το καρμικό μάθημα αυτής της σχέσης με γλαφυρό, διαισθητικό και βαθύ τρόπο.
    """
    return generate_ai_text(prompt)


def ask_caterpillar_chat(previous_report, question, lang="el"):
    prompt = f"""
    {SYSTEM_PERSONA}
    
    Γλώσσα: {"Ελληνικά" if lang == "el" else "English"}
    Προηγούμενη Ανάλυση: {previous_report}
    Ερώτηση Χρήστη: {question}
    
    Απάντησε με ζεστό, κατατοπιστικό και αστρολογικά τεκμηριωμένο ύφος.
    """
    return generate_ai_text(prompt)


def clear_ai_cache():
    pass
