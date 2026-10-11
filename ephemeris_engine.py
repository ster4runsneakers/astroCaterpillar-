# ephemeris_engine.py
import datetime
import math

PLANETS = [
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
]
DEFAULT_TZ = "Europe/Athens"

try:
    import swisseph as swe
    HAS_SWE = True
except Exception:
    swe = None
    HAS_SWE = False

try:
    from zoneinfo import ZoneInfo
    HAS_ZONEINFO = True
except Exception:
    ZoneInfo = None
    HAS_ZONEINFO = False


def extract_deg(val):
    if isinstance(val, dict):
        return float(val.get("deg", 0.0))
    return float(val)


def _local_to_utc(year, month, day, hour, minute, tz_name=DEFAULT_TZ):
    if HAS_ZONEINFO and tz_name:
        try:
            tz = ZoneInfo(tz_name)
            local_dt = datetime.datetime(year, month, day, hour, minute, tzinfo=tz)
            return local_dt.astimezone(datetime.timezone.utc)
        except Exception:
            pass
    return datetime.datetime(year, month, day, hour, minute, tzinfo=datetime.timezone.utc)


def _hour_parts(hour_decimal):
    hour = int(hour_decimal) % 24
    minute = int(round((hour_decimal - int(hour_decimal)) * 60))
    if minute >= 60:
        hour = (hour + 1) % 24
        minute -= 60
    if minute < 0:
        minute = 0
    return hour, minute


def julian_day(year, month, day, hour_decimal):
    y, m = year, month
    if m <= 2:
        y -= 1
        m += 12
    A = math.floor(y / 100)
    B = 2 - A + math.floor(A / 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + day + B - 1524.5
    jd += hour_decimal / 24.0
    return jd


def _approx_planet_deg(planet_name, T):
    if planet_name == "Sun":
        L0 = 280.46646 + 36000.76983 * T
        M = 357.52911 + 35999.05029 * T
        C = (1.914602 - 0.004817 * T) * math.sin(math.radians(M))
        C += (0.019993 - 0.000101 * T) * math.sin(math.radians(2 * M))
        return (L0 + C) % 360.0
    if planet_name == "Moon":
        L = 218.316 + 13.176396 * (T * 36525)
        M = 134.963 + 13.064993 * (T * 36525)
        deg = L + 6.289 * math.sin(math.radians(M))
        return deg % 360.0
    speeds = {
        "Mercury": 4.15201, "Venus": 1.62549, "Mars": 0.52402,
        "Jupiter": 0.08308, "Saturn": 0.03346, "Uranus": 0.01173,
        "Neptune": 0.00598, "Pluto": 0.00396,
    }
    base_deg = {
        "Mercury": 252.25, "Venus": 181.98, "Mars": 355.45,
        "Jupiter": 34.40, "Saturn": 50.08, "Uranus": 314.05,
        "Neptune": 304.35, "Pluto": 238.92,
    }
    days = T * 36525.0
    sp = speeds.get(planet_name, 0.1)
    b = base_deg.get(planet_name, 0.0)
    retro_phase = math.sin(math.radians(days * sp * 0.5)) * 6.0
    return (b + days * sp + retro_phase) % 360.0


def _positions_approx(year, month, day, hour_decimal):
    jd = julian_day(year, month, day, hour_decimal)
    T = (jd - 2451545.0) / 36525.0
    T_next = T + (1.0 / 36525.0)
    positions = {}
    for p in PLANETS:
        deg = _approx_planet_deg(p, T)
        deg_next = _approx_planet_deg(p, T_next)
        diff = (deg_next - deg) % 360.0
        is_retro = (diff > 180.0) and p not in ("Sun", "Moon")
        positions[p] = {"deg": round(deg, 2), "is_retro": is_retro}
    return positions


def _positions_swe(year, month, day, hour_decimal, tz_name=DEFAULT_TZ):
    hour, minute = _hour_parts(hour_decimal)
    utc_dt = _local_to_utc(year, month, day, hour, minute, tz_name)
    hour_ut = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_ut)
    bodies = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
        "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO, "North Node": swe.TRUE_NODE,
    }
    try:
        bodies["Chiron"] = swe.CHIRON
    except Exception:
        pass
    positions = {}
    flags = swe.FLG_MOSEPH | swe.FLG_SPEED  # δεν χρειάζεται αρχεία .se1
    for name, body in bodies.items():
        try:
            xx, _ret = swe.calc_ut(jd_ut, body, flags)
        except Exception:
            # π.χ. Chiron χρειάζεται εξωτερικό αρχείο — παραλείπεται, ΔΕΝ ρίχνει όλο τον χάρτη
            continue
        lon = xx[0] % 360.0
        speed = xx[3]
        positions[name] = {
            "deg": round(lon, 4),
            "is_retro": bool(speed < 0) and name not in ("Sun", "Moon"),
            "speed": round(speed, 5),
        }
    if not all(p in positions for p in PLANETS):
        raise RuntimeError("Λείπουν πλανήτες από τον υπολογισμό Swiss Ephemeris")
    return positions


LAST_ENGINE = "unknown"


def _positions_skyfield(year, month, day, hour_decimal, tz_name=DEFAULT_TZ):
    """Ακριβής εφεδρική μέθοδος (JPL DE421 μέσω Skyfield) όταν η Swiss Ephemeris αποτύχει."""
    import os
    from skyfield.api import Loader
    from skyfield.framelib import ecliptic_frame
    hour, minute = _hour_parts(hour_decimal)
    utc_dt = _local_to_utc(year, month, day, hour, minute, tz_name)
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".skyfield_data")
    os.makedirs(base, exist_ok=True)
    load = Loader(base, verbose=False)
    eph = load("de421.bsp")
    ts = load.timescale()
    t = ts.from_datetime(utc_dt)
    t2 = ts.from_datetime(utc_dt + datetime.timedelta(hours=12))
    earth = eph["earth"]
    names = {
        "Sun": "sun", "Moon": "moon", "Mercury": "mercury", "Venus": "venus",
        "Mars": "mars", "Jupiter": "jupiter barycenter", "Saturn": "saturn barycenter",
        "Uranus": "uranus barycenter", "Neptune": "neptune barycenter",
        "Pluto": "pluto barycenter",
    }
    out = {}
    for p, key in names.items():
        l1 = earth.at(t).observe(eph[key]).apparent().frame_latlon(ecliptic_frame)[1].degrees
        l2 = earth.at(t2).observe(eph[key]).apparent().frame_latlon(ecliptic_frame)[1].degrees
        d = (l2 - l1 + 180.0) % 360.0 - 180.0
        out[p] = {"deg": round(l1 % 360.0, 4), "is_retro": bool(d < 0) and p not in ("Sun", "Moon")}
    return out


def calculate_natal_positions(year, month, day, hour_decimal, tz_name=DEFAULT_TZ):
    global LAST_ENGINE
    if HAS_SWE:
        try:
            res = _positions_swe(year, month, day, hour_decimal, tz_name)
            LAST_ENGINE = "swisseph"
            return res
        except Exception:
            pass
    try:
        res = _positions_skyfield(year, month, day, hour_decimal, tz_name)
        LAST_ENGINE = "skyfield"
        return res
    except Exception:
        pass
    LAST_ENGINE = "approx"
    return _positions_approx(year, month, day, hour_decimal)


def calculate_houses(year, month, day, utc_hour, lat, lon, tz_name=None):
    if tz_name and HAS_SWE:
        hour, minute = _hour_parts(utc_hour)
        utc_dt = _local_to_utc(year, month, day, hour, minute, tz_name)
        hour_ut = utc_dt.hour + utc_dt.minute / 60.0
        jul_day = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_ut)
    elif HAS_SWE:
        jul_day = swe.julday(year, month, day, utc_hour)
    else:
        # Equal houses fallback from approximate Sun + dummy ASC
        jd = julian_day(year, month, day, utc_hour)
        T = (jd - 2451545.0) / 36525.0
        sun = _approx_planet_deg("Sun", T)
        ramc = (sun + lon) % 360.0
        houses = {f"House_{i+1}": (ramc + i * 30.0) % 360.0 for i in range(12)}
        houses["Asc"] = houses["House_1"]
        houses["MC"] = houses["House_10"]
        return houses

    houses_cusps, ascmc = swe.houses(jul_day, lat, lon, b"P")
    houses = {f"House_{i+1}": houses_cusps[i] % 360.0 for i in range(12)}
    houses["House_1"] = ascmc[0] % 360.0
    houses["Asc"] = ascmc[0] % 360.0
    houses["MC"] = ascmc[1] % 360.0
    return houses


def retro_planets(raw_positions, year, month, day, hour_decimal, tz_name=DEFAULT_TZ):
    """Επιστρέφει λίστα αγγλικών ονομάτων αναδρόμων πλανητών.
    Αν τα αποθηκευμένα δεδομένα δεν έχουν σημαία αναδρομής, ξαναϋπολογίζονται."""
    src = raw_positions or {}
    if not any(isinstance(v, dict) and "is_retro" in v for v in src.values()):
        try:
            src = calculate_natal_positions(year, month, day, hour_decimal, tz_name=tz_name)
        except Exception:
            src = raw_positions or {}
    return [p for p, v in src.items() if isinstance(v, dict) and v.get("is_retro")]
