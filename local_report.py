# local_report.py - εφεδρική ανάλυση χωρίς AI (απλά ελληνικά)
from interpretations_el import get_sign_from_degrees
from narrative_el import build_rich_summary


def _deg(v):
    return float(v.get("deg", 0.0)) if isinstance(v, dict) else float(v)


def _sign_id(deg):
    sign_en, _ = get_sign_from_degrees(_deg(deg))
    return str(sign_en).lower()


def build_local_natal(name, natal_pos, houses):
    sun = natal_pos.get("Sun")
    moon = natal_pos.get("Moon")
    if sun is None or moon is None:
        return ""
    asc = (houses or {}).get("Asc")
    asc_id = _sign_id(asc) if asc is not None else None
    return build_rich_summary(_sign_id(sun), _sign_id(moon), asc_id, name or "")
