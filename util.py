"""Utility helpers for data persistence.

This module contains the small, synchronous helpers used by the demo
application to load and save the `patients.json` file. Keeping these in a
separate module makes `main.py` easier to read and test.
"""
from typing import Any, Dict
import json


def load_data() -> Dict[str, Any]:
    """Load patients from `patients.json`.

    Returns the raw dictionary as stored on disk. The function raises the
    usual IO errors if the file is missing or invalid JSON — callers can
    handle or propagate those as needed.
    """
    with open("patients.json", "r") as f:
        return json.load(f)


def save_data(data: Dict[str, Any]) -> None:
    """Write the full patients dictionary back to `patients.json`.

    This overwrites the file. It's intentionally simple for the demo. In a
    production setting you'd add atomic writes and concurrency controls.
    """
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=2)
