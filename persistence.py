# persistence.py - ανθεκτικό backup προφίλ (Streamlit Cloud: ο δίσκος σβήνει σε κάθε restart)
# Σειρά επαναφοράς: 1) GitHub Gist (αν υπάρχει GITHUB_TOKEN στα Secrets)  2) αρχείο profiles_backup.json στο repo
import json
import os

import requests

GIST_DESC = "astrocaterpillar-backup"
GIST_FILE = "astro_profiles.json"
BACKUP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles_backup.json")
_API = "https://api.github.com"


def _hdr(token):
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}


def find_gist_id(token):
    r = requests.get(f"{_API}/gists?per_page=100", headers=_hdr(token), timeout=15)
    r.raise_for_status()
    for g in r.json():
        if g.get("description") == GIST_DESC and GIST_FILE in (g.get("files") or {}):
            return g["id"]
    return None


def push_gist(token, json_text):
    """Αποθηκεύει το JSON σε ΜΥΣΤΙΚΟ gist (δημιουργείται αυτόματα). Επιστρέφει (ok, μήνυμα)."""
    try:
        gid = find_gist_id(token)
        payload = {"files": {GIST_FILE: {"content": json_text}}}
        if gid:
            r = requests.patch(f"{_API}/gists/{gid}", headers=_hdr(token), json=payload, timeout=20)
        else:
            payload.update({"description": GIST_DESC, "public": False})
            r = requests.post(f"{_API}/gists", headers=_hdr(token), json=payload, timeout=20)
        r.raise_for_status()
        return True, "Αποθηκεύτηκε στο GitHub backup."
    except Exception as e:  # δεν πρέπει ποτέ να ρίξει την εφαρμογή
        return False, f"Το GitHub backup απέτυχε: {type(e).__name__}"


def pull_gist(token):
    try:
        gid = find_gist_id(token)
        if not gid:
            return None
        r = requests.get(f"{_API}/gists/{gid}", headers=_hdr(token), timeout=20)
        r.raise_for_status()
        f = r.json()["files"][GIST_FILE]
        if f.get("truncated") and f.get("raw_url"):
            return requests.get(f["raw_url"], headers=_hdr(token), timeout=20).text
        return f.get("content")
    except Exception:
        return None


def read_file_backup():
    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as fh:
            return fh.read()
    except Exception:
        return None


def validate_backup(text):
    """Αληθές αν το κείμενο είναι έγκυρη λίστα προφίλ."""
    try:
        data = json.loads(text)
        return isinstance(data, list) and len(data) > 0
    except Exception:
        return False
