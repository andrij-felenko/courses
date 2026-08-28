import re, sys
from dataclasses import dataclass
from pathlib import Path
import yaml   # pip install pyyaml

ZONE = "node.labels.zone"      # мітка вузла: в якій зоні доступності він стоїть

# ── 1. База + оверлей середовища → глибоке злиття ────────────────────────────
#    (те саме, що робить `docker compose -f base -f over config`)
def load_stack(*paths: str) -> dict:
    stack: dict = {}
    for p in paths:
        layer = yaml.safe_load(Path(p).read_text("utf-8")) or {}
        stack = deep_merge(stack, layer)
    return stack

def deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        merge = isinstance(v, dict) and isinstance(out.get(k), dict)
        out[k] = deep_merge(out[k], v) if merge else v
    return out

# ── 2. У яких зонах placement ГАРАНТУЄ копії ─────────────────────────────────
def zone_cover(deploy: dict) -> tuple[set[str], bool]:
    place = deploy.get("placement") or {}
    pinned = {m.group(1)
              for c in (place.get("constraints") or [])
              if (m := re.search(rf"{re.escape(ZONE)}\s*==\s*(\S+)", c))}
    spreads = any((p or {}).get("spread") == ZONE
                  for p in (place.get("preferences") or []))
    return pinned, spreads          # {зони під твердим constraint}, чи є spread

# ── 3. Вердикт на один логічний контейнер ────────────────────────────────────
@dataclass
class Report:
    name: str
    copies: int
    verdict: str        # single | ok | warn | fail
    note: str

def judge(name: str, spec: dict) -> Report:
    deploy = spec.get("deploy") or {}
    copies = int(deploy.get("replicas", 1))
    zones, spreads = zone_cover(deploy)
    if copies <= 1:
        return Report(name, copies, "single", "одна копія — надлишковості нема")
    if len(zones) >= 2 or spreads:
        return Report(name, copies, "ok", "копії рознесено по зонах")
    if len(zones) == 1:
        return Report(name, copies, "fail",
                      f"усі прибито до зони {next(iter(zones))} — надлишковість уявна")
    return Report(name, copies, "warn",
                  "нема правила зон — планувальник може скласти копії в одну зону")

def analyze(stack: dict) -> list[Report]:
    services = (stack.get("services") or {}).items()
    return [judge(n, s or {}) for n, s in sorted(services)]

# ── 4. Паритет: набір логічних сервісів мусить збігатися між середовищами ─────
def parity_gap(dev: dict, prod: dict) -> set[str]:
    d = set(dev.get("services") or {})
    p = set(prod.get("services") or {})
    return d ^ p                     # симетрична різниця: хто є лише в одному

# ── 5. Гейт CI: fail або зламаний паритет валить збірку (код виходу 1) ────────
if __name__ == "__main__":
    dev  = load_stack("compose.yaml", "compose.dev.yaml")
    prod = load_stack("compose.yaml", "compose.prod.yaml")
    mark = {"ok": "OK  ", "single": "·   ", "warn": "WARN", "fail": "FAIL"}
    bad = False
    print("== prod ==")
    for r in analyze(prod):
        print(f"{mark[r.verdict]} {r.name:7} копій: {r.copies}  {r.note}")
        bad |= r.verdict == "fail"
    if gap := parity_gap(dev, prod):
        print("PARITY  лише в одному середовищі:", ", ".join(sorted(gap)))
        bad = True
    sys.exit(1 if bad else 0)
