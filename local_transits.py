# local_transits.py - διελεύσεις χωρίς AI, από τη μηχανή υπολογισμού της εφαρμογής (απλά ελληνικά)
import datetime

from ephemeris_engine import calculate_natal_positions

TRANSIT_PLANETS = ["Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
NATAL_POINTS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                "Uranus", "Neptune", "Pluto", "Asc", "MC"]

PNAME = {
    "Sun": "Ήλιος", "Moon": "Σελήνη", "Mercury": "Ερμής", "Venus": "Αφροδίτη", "Mars": "Άρης",
    "Jupiter": "Δίας", "Saturn": "Κρόνος", "Uranus": "Ουρανός", "Neptune": "Ποσειδώνας",
    "Pluto": "Πλούτωνας", "Asc": "Ωροσκόπος", "MC": "Μεσουράνημα",
}
# (όνομα όψης, ορίζουσα γωνία, τόνος)
ASPECTS = [
    (0.0, "σε σύνοδο με", "conj"),
    (60.0, "σε εξάγωνο με", "flow"),
    (90.0, "σε τετράγωνο με", "tense"),
    (120.0, "σε τρίγωνο με", "flow"),
    (180.0, "σε αντίθεση με", "tense"),
]
ORB = {"Mars": 1.5, "Jupiter": 2.0, "Saturn": 2.0, "Uranus": 2.0, "Neptune": 2.0, "Pluto": 2.0}
WEIGHT = {"Pluto": 6, "Neptune": 5, "Uranus": 5, "Saturn": 5, "Jupiter": 3, "Mars": 1}
ASPECT_WEIGHT = {"conj": 3, "tense": 2, "flow": 1}

FLOW = {
    "Mars": "παίρνεις ενέργεια και κουράγιο να κινηθείς",
    "Jupiter": "ανοίγουν ευκαιρίες και ανεβαίνει η αυτοπεποίθησή σου",
    "Saturn": "χτίζεις σταθερά και με υπομονή, και αυτό αντέχει",
    "Uranus": "έρχονται ευχάριστες αλλαγές και φρέσκιες ιδέες",
    "Neptune": "η διαίσθηση και η φαντασία δουλεύουν δυνατά",
    "Pluto": "έχεις δύναμη να αλλάξεις κάτι σε βάθος",
}
TENSE = {
    "Mars": "υπάρχει ένταση και εκνευρισμός — πρόσεχε τις βιαστικές κινήσεις",
    "Jupiter": "τα παρατραβάς· πρόσεχε υπερβολές και υποσχέσεις που δεν θα κρατήσεις",
    "Saturn": "νιώθεις πίεση και ευθύνες, και ό,τι κάνεις θέλει περισσότερο κόπο",
    "Uranus": "έρχονται ξαφνικές ανατροπές — κράτα λίγη ελαστικότητα",
    "Neptune": "μπερδεύεσαι και δεν βλέπεις καθαρά — μην αποφασίζεις βιαστικά",
    "Pluto": "βγαίνουν στην επιφάνεια θέματα ελέγχου και βαθιάς αλλαγής",
}
CONJ = {
    "Mars": "δυνατή ενέργεια, καλή στιγμή για μια καθαρή αρχή",
    "Jupiter": "ευκαιρία για ανάπτυξη — αρκεί να κινηθείς",
    "Saturn": "σοβαρό σημείο καμπής: ευθύνη, αλλά και πραγματική ωρίμανση",
    "Uranus": "ξεκινά μια αλλαγή που δύσκολα θα γυρίσει πίσω",
    "Neptune": "έμπνευση και ομίχλη μαζί — κράτα τα πόδια στη γη",
    "Pluto": "μεγάλη μεταμόρφωση σε αργό ρυθμό, που ζητά ειλικρίνεια με τον εαυτό σου",
}
AREA = {
    "Sun": "ταυτότητα και προσωπική κατεύθυνση",
    "Moon": "συναισθήματα, σπίτι, οικογένεια",
    "Mercury": "σκέψη, επικοινωνία, συμφωνίες",
    "Venus": "σχέσεις, αγάπη, χρήματα",
    "Mars": "δράση, ενέργεια, φιλοδοξία",
    "Jupiter": "ανάπτυξη, ευκαιρίες, πίστη στον εαυτό",
    "Saturn": "όρια, δουλειά, ευθύνες",
    "Uranus": "ελευθερία και αλλαγές",
    "Neptune": "όνειρα, διαίσθηση, αυταπάτες",
    "Pluto": "βαθιά μοτίβα και έλεγχος",
    "Asc": "πώς εμφανίζεσαι και πώς ξεκινάς πράγματα",
    "MC": "καριέρα και δημόσια εικόνα",
}
PACC = {
    "Sun": "Ήλιο", "Moon": "Σελήνη", "Mercury": "Ερμή", "Venus": "Αφροδίτη", "Mars": "Άρη",
    "Jupiter": "Δία", "Saturn": "Κρόνο", "Uranus": "Ουρανό", "Neptune": "Ποσειδώνα",
    "Pluto": "Πλούτωνα", "Asc": "Ωροσκόπο", "MC": "Μεσουράνημα",
}
MONTHS_EL = ["Ιανουάριος", "Φεβρουάριος", "Μάρτιος", "Απρίλιος", "Μάιος", "Ιούνιος",
             "Ιούλιος", "Αύγουστος", "Σεπτέμβριος", "Οκτώβριος", "Νοέμβριος", "Δεκέμβριος"]


def _deg(v):
    return float(v.get("deg", 0.0)) if isinstance(v, dict) else float(v)


def _sep(a, b):
    d = abs(a - b) % 360.0
    return 360.0 - d if d > 180.0 else d


def _sentence(tp, kind, npnt):
    if kind == "conj":
        txt = CONJ[tp]
    elif kind == "flow":
        txt = "ευνοϊκή περίοδος: " + FLOW[tp]
    else:
        txt = "δύσκολη περίοδος: " + TENSE[tp]
    return f"{txt}. Αφορά: {AREA.get(npnt, '')}."


def compute_transit_windows(natal, start_date, days=180, step=2):
    """natal: {σημείο: μοίρες}. Επιστρέφει λίστα παραθύρων όψεων (χωρίς AI).
    Υπολογίζει τις θέσεις των πλανητών ανά `step` ημέρες (12:00)."""
    natal = {k: _deg(v) for k, v in natal.items() if k in NATAL_POINTS}
    samples = []
    d = start_date
    end = start_date + datetime.timedelta(days=days)
    while d <= end:
        try:
            pos = calculate_natal_positions(d.year, d.month, d.day, 12.0)
        except Exception:
            pos = None
        samples.append((d, {p: _deg(v) for p, v in pos.items()} if pos else None))
        d += datetime.timedelta(days=step)

    # ανοιχτά παράθυρα ανά (πλανήτης, όψη, φυσικό σημείο)
    open_w, done = {}, []

    def close(key):
        w = open_w.pop(key, None)
        if w:
            done.append(w)

    for d, pos in samples:
        hit_now = set()
        if pos:
            for tp in TRANSIT_PLANETS:
                if tp not in pos:
                    continue
                for npnt, ndeg in natal.items():
                    s = _sep(pos[tp], ndeg)
                    for ang, _label, kind in ASPECTS:
                        orb = abs(s - ang)
                        if orb <= ORB[tp]:
                            key = (tp, ang, npnt)
                            hit_now.add(key)
                            w = open_w.get(key)
                            if w is None:
                                open_w[key] = {"tp": tp, "ang": ang, "kind": kind, "np": npnt,
                                               "first": d, "last": d, "best_orb": orb, "best_day": d}
                            else:
                                w["last"] = d
                                if orb < w["best_orb"]:
                                    w["best_orb"], w["best_day"] = orb, d
        for key in list(open_w.keys()):
            if key not in hit_now:
                close(key)
    for key in list(open_w.keys()):
        close(key)
    label = {a: l for a, l, _ in ASPECTS}
    for w in done:
        w["label"] = label[w["ang"]]
        w["best_orb"] = round(w["best_orb"], 2)
    return done


def _score(w):
    return WEIGHT[w["tp"]] * ASPECT_WEIGHT[w["kind"]] + (3 if w["np"] in ("Sun", "Moon", "Asc", "MC") else 0)


def monthly_summary_markdown(windows, start_date, months=6, per_month=6):
    """Απλά ελληνικά, ομαδοποίηση ανά μήνα κορύφωσης."""
    seen = {}
    by_month = {}
    for w in sorted(windows, key=lambda x: x["best_day"]):
        k = (w["tp"], w["ang"], w["np"])
        w["again"] = k in seen
        seen[k] = True
        by_month.setdefault((w["best_day"].year, w["best_day"].month), []).append(w)
    out = []
    y, m = start_date.year, start_date.month
    for _ in range(months):
        items = sorted(by_month.get((y, m), []), key=lambda w: -_score(w))[:per_month]
        items = sorted(items, key=lambda w: w["best_day"])
        block = [f"#### {MONTHS_EL[m - 1]} {y}"]
        if not items:
            block.append("Ήσυχος μήνας — καμία μεγάλη διέλευση προς τον χάρτη σου.")
        for w in items:
            a = max(w["first"], start_date)
            rng = (f"{a.strftime('%d/%m')}–{w['last'].strftime('%d/%m')}"
                   if a != w["last"] else a.strftime('%d/%m'))
            again = " (ξανά — αναδρομή)" if w.get("again") else ""
            block.append(
                f"- **{PNAME[w['tp']]} {w['label']} {PACC[w['np']]}** · κορύφωση ~{w['best_day'].strftime('%d/%m')}"
                f" (περίοδος {rng}){again}\n  {_sentence(w['tp'], w['kind'], w['np'])}"
            )
        out.append("\n".join(block))
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return "\n\n".join(out)


def month_brief(windows, year, month, limit=5):
    """Σύντομο κείμενο για prompt του chat (τι συμβαίνει τον μήνα)."""
    items = [w for w in windows if (w["best_day"].year, w["best_day"].month) == (year, month)]
    items = sorted(items, key=lambda w: -_score(w))[:limit]
    return "; ".join(f"{PNAME[w['tp']]} {w['label']} {PACC[w['np']]} (~{w['best_day'].strftime('%d/%m')})"
                     for w in items) or "καμία μεγάλη διέλευση"
