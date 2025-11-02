from __future__ import annotations
from datetime import datetime
from typing import Iterable, List

def parse_date(s: str) -> str:
    """
    Accepts 'YYYY-MM-DD'. Raises ValueError if invalid.
    """
    s = s.strip()
    if not s:
        return ""
    dt = datetime.strptime(s, "%Y-%m-%d")
    return dt.strftime("%Y-%m-%d")

def iso_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def print_table(headers: List[str], rows: Iterable[Iterable[str]]):
    cols = [list(map(str, [h] + [r[i] for r in rows])) for i, h in enumerate(headers)]
    widths = [max(len(x) for x in col) for col in cols]
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for r in rows:
        print(fmt.format(*r))
