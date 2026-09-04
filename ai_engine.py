# ai_engine.py - AstroCaterpillar AI Engine
import os
import time
import sqlite3
import requests
import streamlit as st
from google import genai

DB_FILE = "astro_data.db"

def _init_cache_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ai_cache (
            cache_key TEXT PRIMARY KEY,
            response_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

_init_cache_db()

def _get_cached_response(key: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT response_text FROM ai_cache WHERE cache_key = ?', (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def _set_cached_response(key: str, text: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO ai_cache (cache_key, response_text) VALUES (?, ?)', (key, text))
    conn.commit()
    conn.close()

def clear_ai_cache():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM ai_cache')
    conn.commit()
    conn.close()

def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

def _call_gemini_safe(prompt: str) -> str:
    client = get_gemini_client()
    models = ['gemini-2.5-flash', 'gemini-1.5-pro', 'gemini-1.5-flash']
    
    for model_name in models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception:
                time.sleep(1)
                continue

    return "⚠️ Οι εξυπηρετητές AI είναι προσωρινά υπερφορτωμένοι. Παρακαλώ δοκιμάστε ξανά σε λίγα δευτερόλεπτα."

def call_deepseek_llm(prompt: str) -> str:
    openrouter_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
    deepseek_key = st.secrets.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")

    if openrouter_key:
        try:
            res = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek/deepseek-r1:free",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4
                },
                timeout=45
            )
            if res.status_code == 200:
                data = res.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
        except Exception:
            pass

    if deepseek_key:
        try:
            res = requests.post(
                url="https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {deepseek_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4
                },
                timeout=45
            )
            if res.status_code == 200:
                data = res.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
        except Exception:
            pass

    return _call_gemini_safe(prompt)

def run_dual_agent_pipeline(raw_data_prompt: str, persona_instructions: str, lang: str = "el", cache_key: str = None) -> str:
    if cache_key:
        full_cache_key = f"{cache_key}_{lang}"
        cached = _get_cached_response(full_cache_key)
        if cached:
            return cached

    if lang == "en":
        prompt_synthesis = f"""
        You are AstroCaterpillar – an intuitive, warm, and deeply insightful astrological advisor.
        
        YOUR STYLE & PERSONA:
        1. Combine the warm, communicative directness of top media astrologers with deep psychological analysis.
        2. Speak directly to the reader in a compassionate, friendly, and practical tone.
        3. Explain complex planetary energy through everyday life examples. Avoid heavy technical jargon or dry texts.
        4. Be deeply honest, revealing both strengths and challenges clearly.

        ANALYSIS PURPOSE:
        {persona_instructions}

        ASTROLOGICAL DATA MATRIX:
        {raw_data_prompt}

        OUTPUT STRUCTURE (Use English):
        - **In a Nutshell:** A warm, intuitive overview of the personal chart.
        - **Inner Strengths & Life Challenges:** Clear, psychological insights into potential and pitfalls.
        - **Practical Guidance:** Direct, actionable advice for everyday life.
        """
    else:
        prompt_synthesis = f"""
        Είσαι ο AstroCaterpillar – ένας ζεστός, διαισθητικός και βαθιά ψυχογραφικός αστρολογικός σύμβουλος.
        
        ΥΦΟΣ ΚΑΙ ΠΡΟΣΩΠΙΚΟΤΗΤΑ (Στυλ Λίτσας Πατέρα & Ισμήνης Καραλή):
        1. Συνδύασε τον ζεστό, επικοινωνιακό και άμεσο λόγο με βαθιά ψυχολογική και διεισδυτική ανάλυση.
        2. Μίλα στον αναγνώστη σαν έναν δικό σου άνθρωπο, με ενσυναίσθηση, θετική ενέργεια αλλά και απόλυτη ειλικρίνεια.
        3. Εξήγησε τις πλανητικές επιρροές μέσα από παραδείγματα της καθημερινής ζωής. Απέφευγε την ψυχρή τεχνοκρατική γλώσσα και τους βαρύγδουπους όρους.
        4. Ανέδειξε τόσο τα χαρίσματα όσο και τα τρωτά σημεία με τρόπο που δίνει ελπίδα και καθαρή κατεύθυνση.

        ΣΤΟΧΟΣ ΑΝΑΛΥΣΗΣ:
        {persona_instructions}

        ΠΡΩΤΟΓΕΝΗ ΔΕΔΟΜΕΝΑ (DATA MATRIX):
        {raw_data_prompt}

        ΔΟΜΗ ΑΠΑΝΤΗΣΗΣ (Στα Ελληνικά):
        - **Με μια ματιά:** Μια ζεστή, συνοπτική εικόνα της προσωπικότητας και της ενέργειας.
        - **Δυνάμεις & Εσωτερικές Προκλήσεις:** Ψυχογραφική ανάλυση των δυνατών σημείων και των παγίδων.
        - **Πρακτική Συμβουλή Ζωής:** Καθαρή, εφαρμόσιμη συμβουλή για την καθημερινότητα.
        """

    final_output = call_deepseek_llm(prompt_synthesis)

    if cache_key and final_output and not final_output.startswith("⚠️"):
        _set_cached_response(f"{cache_key}_{lang}", final_output)

    return final_output

def ask_caterpillar_chat(report_context: str, user_question: str, lang: str = "el") -> str:
    if lang == "en":
        prompt = f"""
        You are AstroCaterpillar. Answer the user's question based strictly on the provided natal context.
        Maintain a warm, intuitive, and highly encouraging tone.
        
        CONTEXT:
        {report_context}

        USER QUESTION:
        {user_question}
        """
    else:
        prompt = f"""
        Είσαι ο AstroCaterpillar. Απάντησε στην ερώτηση του χρήστη με βάση την παρακάτω ανάλυση.
        Διατήρησε ένα ζεστό, επικοινωνιακό και ενθαρρυντικό ύφος.

        ΑΝΑΛΥΣΗ:
        {report_context}

        ΕΡΩΤΗΣΗ ΧΡΗΣΤΗ:
        {user_question}
        """
    return call_deepseek_llm(prompt)

# --- EXPORTED MODULE WRAPPERS ---
def analyze_natal_chart_ai(name, positions_formatted, house_info, cz_info, elem_info, aspects_formatted, lang="el"):
    raw_data = (
        f"--- PLANETARY POSITIONS ---\n{positions_formatted}\n\n"
        f"--- HOUSES DATA ---\n{house_info}\n\n"
        f"--- PLANETARY ASPECTS ---\n{aspects_formatted}\n\n"
        f"--- ELEMENTS & MODALITIES ---\n{elem_info}\n\n"
        f"--- CHINESE ZODIAC ---\n{cz_info}"
    )
    instructions = f"Full Natal & Psychological Analysis for {name}."
    return run_dual_agent_pipeline(raw_data, instructions, lang=lang, cache_key=f"natal_{name}")

def analyze_synastry_ai(person_a, person_b, aspects_formatted, lang="el"):
    return run_dual_agent_pipeline(f"ASPECTS:\n{aspects_formatted}", f"Synastry Analysis between {person_a} & {person_b}.", lang=lang, cache_key=f"syn_{person_a}_{person_b}")

def analyze_transits_ai(person, target_date, transit_hits_formatted, lang="el"):
    return run_dual_agent_pipeline(f"Date: {target_date}\n{transit_hits_formatted}", f"Transits Analysis for {person}.", lang=lang, cache_key=f"tr_{person}_{target_date}")
      
