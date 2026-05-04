"""
persistence.py — Save/load leaderboard and settings for TSIS 3 Racer
"""

import json
import os
from datetime import datetime

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

# ── Default settings ──────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  [50, 100, 220],   # RGB blue
    "difficulty": "normal",          # easy / normal / hard
}


# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

def load_settings():
    """Load settings from JSON; fall back to defaults for missing keys."""
    if not os.path.exists(SETTINGS_FILE):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults so new keys are never missing
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    """Persist settings dict to JSON."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# LEADERBOARD
# ─────────────────────────────────────────────────────────────────────────────

def load_leaderboard():
    """Load leaderboard list from JSON (list of dicts, sorted by score desc)."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_leaderboard(entries):
    """Persist leaderboard list to JSON."""
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def add_entry(username, score, distance, coins):
    """Add a new entry, keep top 10, re-save."""
    entries = load_leaderboard()
    entries.append({
        "name":     username,
        "score":    score,
        "distance": distance,
        "coins":    coins,
        "date":     datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    # Sort by score descending and keep top 10
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:10]
    save_leaderboard(entries)
    return entries