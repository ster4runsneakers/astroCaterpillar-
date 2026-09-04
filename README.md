# 🐛 AstroCaterpillar AI

[EL] Το **AstroCaterpillar AI** είναι μια αυτόνομη, δεδομενοκεντρική εφαρμογή αστρολογικής ανάλυσης, στρατηγικών διελεύσεων και συναστρίας. Σχεδιασμένη με βάση τις αρχές του **Self-Custody** (ιδιοκτησία δεδομένων), συνδυάζει αστρονομικούς υπολογισμούς υψηλής ακρίβειας (Swiss Ephemeris) με διαδραστικά γραφήματα και διεισδυτική AI αφήγηση μέσω του Google Gemini API.

[EN] **AstroCaterpillar AI** is an autonomous, data-centric micro-app for astrological calculations, strategic transits, and synastry analysis. Built upon **Self-Custody** data architecture, it combines high-precision astronomical mechanics (Swiss Ephemeris) with interactive visualizations and deep AI narrative analysis via the Google Gemini API.

---

## 🌟 Βασικά Χαρακτηριστικά / Key Features

### 🌌 1. Γενέθλιος Χάρτης & Αναλύσεις / Natal Chart & Indicators
* **Swiss Ephemeris Precision:** Υπολογισμοί ακριβείας για πλανήτες, αιχμές 12 οίκων, στοιχεία, ποιότητες και κινεζικό ωροσκόπιο.
* **Interactive Plotly Wheel:** Διαδραστικός χάρτης βελτιστοποιημένος για mobile & desktop.
* **AI Natal Interpretation:** Βαθιά, αντικειμενική ψυχογραφική ανάλυση χωρίς υπερβολές.

### 📅 2. Μηνιαίες Διελεύσεις / Monthly Transits
* **Macro-Cycle Tracking:** Εντοπισμός σημαντικών όψεων αργών πλανητών (Άρης έως Πλούτωνας).
* **Strategic Timing:** Στρατηγική αξιολόγηση ευκαιριών και προκλήσεων ανά μήνα/έτος.

### 💞 3. Συναστρία & Bi-Wheel Charts / Synastry & Inter-aspects
* **Dual Wheel Visualization:** Οπτικοποίηση αλληλεπίδρασης δύο γενέθλιων χαρτών.
* **Synastry AI Report & Ebook Export:** Παραγωγή αναλυτικής έκθεσης συμβατότητας και εξαγωγή σε PDF Ebook.

### 💬 4. Διαδραστικό Chat με Ιστορικό / Persistent Multi-turn Chat
* **Context-Aware AI Assistant:** Ο AI Βοηθός θυμάται το ιστορικό της συζήτησης σε κάθε ενότητα (Γενέθλιος, Διελεύσεις, Συναστρία) για συνεχή διάλογο.

### 🔐 5. Ασφάλεια & Privacy (BYOK & Admin Protection)
* **Bring Your Own Key (BYOK):** Οι επισκέπτες μπορούν να εισάγουν το δικό τους δωρεάν Gemini API Key.
* **Admin Master Key Fallback:** Προστασία του κεντρικού API Key, διαθέσιμο μόνο για πιστοποιημένους Admins.
* **Auto Model Fallback Mechanism:** Αυτόματη εναλλαγή μοντέλων (`gemini-2.5-flash` ➔ `gemini-1.5-flash` / `gemini-2.5-pro`) σε περίπτωση εξάντλησης ορίων (429 Rate Limits).

---

## 🛠️ Τεχνολογικό Stack / Tech Stack

* **Frontend / Framework:** Python, Streamlit
* **Astronomical Calculations:** PySwisseph (Swiss Ephemeris)
* **Visualizations:** Plotly, Matplotlib
* **Database:** SQLite (Local Database for Profiles) & JSON Backup/Import
* **AI SDK:** `google-genai` (Google Gemini API)
* **PDF Engines:** ReportLab / WeasyPrint

---

## 🚀 Οδηγίες Εγκατάστασης & Εκτέλεσης / Quick Start

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/AstroCaterpillar.git](https://github.com/your-username/AstroCaterpillar.git)
cd AstroCaterpillar
