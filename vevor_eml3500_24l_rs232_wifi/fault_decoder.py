"""Decode VEVOR EML3500 32-bit fault and warning registers.

This module loads fault and warning code definitions from CSV files and
provides helper functions to translate raw 32-bit register values into
human readable descriptions.
"""

from __future__ import annotations

from pathlib import Path
import csv
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR.parent / "docs"
FAULT_CODES_CSV = DOCS_DIR / "vevor_eml3500_24l_fault_codes.csv"
WARNING_CODES_CSV = DOCS_DIR / "vevor_eml3500_24l_warning_codes.csv"


def _load_codes(path: Path) -> Dict[int, str]:
    """Load bit code mapping from a CSV file."""
    codes: Dict[int, str] = {}
    with path.open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bit_str = (row.get("Bit/Code") or "").strip()
            if not bit_str.startswith("bit"):
                continue
            cleaned = bit_str.replace("bit", "").strip()
            try:
                bit_num = int(cleaned)
            except ValueError:
                continue
            desc = (row.get("Explain") or "").strip()
            codes[bit_num] = desc
    return codes


# Preload mappings
FAULT_CODES = _load_codes(FAULT_CODES_CSV)
WARNING_CODES = _load_codes(WARNING_CODES_CSV)


def _decode(value: int, codes: Dict[int, str]) -> List[str]:
    """Decode set bits in *value* using *codes* mapping."""
    if not codes:
        return []
    base = min(codes)
    decoded: List[str] = []
    for bit, desc in codes.items():
        mask = 1 << (bit - base)
        if value & mask:
            decoded.append(desc)
    return decoded


def decode_faults(value: int) -> List[str]:
    """Return list of fault descriptions for a raw register value."""
    return _decode(value, FAULT_CODES)


def decode_warnings(value: int) -> List[str]:
    """Return list of warning descriptions for a raw register value."""
    return _decode(value, WARNING_CODES)
