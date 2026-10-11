# summary_el.py - σύντομη «Σύνοψη» στην κορυφή του χάρτη (χωρίς AI, απλά ελληνικά)
from interpretations_el import get_sign_from_degrees
from zodiac import get_zodiac_by_id
from narrative_el import SUN_WANT, MOON_NEED, ASC_LOOK

RETRO_SHORT = {
    "Mercury": "Ερμής: σκέφτεσαι βαθιά πριν μιλήσεις, κάνεις δεύτερες σκέψεις",
    "Venus": "Αφροδίτη: ξανακοιτάς τι αξίζει για σένα σε σχέσεις και χρήματα",
    "Mars": "Άρης: η ενέργεια μπαίνει μέσα, δεν ξεσπάς εύκολα",
    "Jupiter": "Δίας: η πίστη και η ανάπτυξη έρχονται από μέσα προς τα έξω",
    "Saturn": "Κρόνος: είσαι αυστηρός με τον εαυτό σου, ο έλεγχος είναι εσωτερικός",
    "Uranus": "Ουρανός: η ανάγκη για ελευθερία βγαίνει πιο ήσυχα, από μέσα",
    "Neptune": "Ποσειδώνας: έντονη διαίσθηση και πιο ιδιωτικά όνειρα",
    "Pluto": "Πλούτωνας: βαθιές αλλαγές που γίνονται μέσα σου, όχι προς τα έξω",
}


def _sign_id(deg):
    return str(get_sign_from_degrees(float(deg))[0]).lower()


def _name(sign_id):
    try:
        return get_zodiac_by_id(sign_id).name_el
    except Exception:
        return sign_id


def build_short_summary(name, natal_pos, houses, retro_en):
    """Επιστρέφει markdown 4-6 γραμμών. Δεν αλλάζει κανέναν υπολογισμό."""
    sun, moon = natal_pos.get("Sun"), natal_pos.get("Moon")
    if sun is None or moon is None:
        return ""
    s_id, m_id = _sign_id(sun), _sign_id(moon)
    asc = (houses or {}).get("Asc")
    lines = []
    who = f"**{name}**, " if name else ""
    lines.append(f"{who}με λίγα λόγια:")
    lines.append(f"- ☀️ **Ήλιος {_name(s_id)}** — κυνηγάς: {SUN_WANT.get(s_id, '')}.")
    lines.append(f"- 🌙 **Σελήνη {_name(m_id)}** — χρειάζεσαι για να ηρεμήσεις: {MOON_NEED.get(m_id, '')}.")
    if asc is not None:
        a_id = _sign_id(asc)
        lines.append(f"- 🌅 **Ωροσκόπος {_name(a_id)}** — οι άλλοι σε βλέπουν ως: {ASC_LOOK.get(a_id, '')}.")
    r = [p for p in (retro_en or []) if p in RETRO_SHORT]
    if r:
        lines.append("- ℞ **Αναδρομικοί:** " + " · ".join(RETRO_SHORT[p] for p in r) + ".")
    else:
        lines.append("- ℞ Κανένας αναδρομικός πλανήτης στον χάρτη σου.")
    return "\n".join(lines)
