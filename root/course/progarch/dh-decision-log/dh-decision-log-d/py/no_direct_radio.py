# fitness/no_direct_radio.py — сторож рішення ADR-007.
# Падає в CI, якщо логіка хаба звертається до радіо повз порт DevicePort.
import ast, pathlib

LOGIC = pathlib.Path("hub/logic")             # правила, стан, сценарії
FORBIDDEN = ("zigbee", "zwave", "matter")     # імена радіо-бібліотек

def offenders():
    for src in LOGIC.rglob("*.py"):
        tree = ast.parse(src.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mod = (getattr(node, "module", "") or
                   "".join(a.name for a in getattr(node, "names", [])))
            if any(r in mod.lower() for r in FORBIDDEN):
                yield src, mod

def test_hub_logic_talks_only_to_port():
    bad = list(offenders())
    assert not bad, (
        "Порушено ADR-007: логіка хаба імпортує радіо напряму:\n" +
        "\n".join(f"  {s}: {m}" for s, m in bad))
