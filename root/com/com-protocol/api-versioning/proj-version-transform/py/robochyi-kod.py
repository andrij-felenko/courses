from dataclasses import dataclass
from typing import Callable, Optional

Req = dict   # {"params": {...}, "body": {...}}
Res = dict   # {"status": int, "body": {...}}

@dataclass
class VersionChange:
    version: str                 # дата набуття чинності (ISO)
    description: str
    up_request: Optional[Callable[[Req], Req]] = None    # форма ДО → форма ПІСЛЯ (запит)
    down_response: Optional[Callable[[Res], Res]] = None  # форма ПІСЛЯ → форма ДО (відповідь)


def _rename_up(r: Req) -> Req:
    b = r["body"]
    if "amount" in b:
        b["total"] = b.pop("amount")
    return r

def _rename_down(r: Res) -> Res:
    b = r["body"]
    if "total" in b:
        b["amount"] = b.pop("total")
    return r

def _cents_up(r: Req) -> Req:
    b = r["body"]
    if isinstance(b.get("total"), (int, float)):
        b["total"] *= 100
    return r

def _cents_down(r: Res) -> Res:
    b = r["body"]
    if isinstance(b.get("total"), (int, float)):
        b["total"] = round(b["total"] / 100)
    return r

# Від найстарішої до найновішої.
changes = [
    VersionChange("2024-02-20", "amount → total", _rename_up, _rename_down),
    VersionChange("2024-11-05", "долари → центи", _cents_up, _cents_down),
]
