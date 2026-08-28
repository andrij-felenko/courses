# fitness/trace_check.py — фітнес-функція на ЦІЛІСНІСТЬ усього сліду рішень DH.
# Запуск із кореня репозиторію:  python fitness/trace_check.py
# Ненульовий код виходу = CI червоний, і в КОЖНОМУ рядку — ім'я винного ADR.
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import ast, re, sys, tokenize, yaml      # yaml: pip install pyyaml — фронт-матер це YAML

ADR_DIR = Path("docs/adr")               # тут лежать записи виду ADR-NNN.md
REPO    = Path(".")                      # корінь репозиторію
LOGIC   = Path("hub/logic")             # правила / стан / сценарії — «мозок» хаба
RADIO   = {"zigbee", "zwave", "matter", "zigpy", "bellows"}  # верхні пакети радіо-стеків
ID_RE   = re.compile(r"ADR-0*(\d+)")     # ловить і ADR-7, і ADR-007; число — канонічний ключ


def canon(num: int) -> str:
    return f"ADR-{num:03d}"               # ЄДИНА форма запису: ADR-007, ніколи ADR-7


@dataclass
class Adr:
    num: int
    status: str
    supersedes: list[int]
    superseded_by: list[int]
    code: list[str]
    view: str
    path: Path

    @property
    def id(self) -> str:
        return canon(self.num)


def front_matter(path: Path) -> dict | None:
    """YAML-шапка між двома рядками «---». Прив'язка до меж рядка береже «---» у тілі."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None                       # не ADR-запис — просто markdown
    return yaml.safe_load(m.group(1)) or {}


def as_nums(raw) -> list[int]:
    """Список ADR-номерів із поля фронт-матера: [ADR-023] чи 'ADR-023' → [23]."""
    if raw is None:
        return []
    items = [raw] if isinstance(raw, (str, int)) else list(raw)
    return [int(ID_RE.search(str(x)).group(1)) for x in items if ID_RE.search(str(x))]


def load_adrs(adr_dir: Path) -> dict[int, Adr]:
    adrs: dict[int, Adr] = {}
    for path in sorted(adr_dir.glob("*.md")):
        meta = front_matter(path)
        if meta is None:
            continue
        m = ID_RE.search(str(meta.get("id", "")))
        if not m:
            raise SystemExit(f"{path}: у фронт-матері бракує поля id виду ADR-NNN")
        num = int(m.group(1))
        adrs[num] = Adr(
            num=num,
            status=str(meta.get("status", "")).strip().lower(),
            supersedes=as_nums(meta.get("supersedes")),
            superseded_by=as_nums(meta.get("superseded-by")),
            code=[str(c) for c in (meta.get("code") or [])],
            view=str(meta.get("view") or ""),
            path=path)
    return adrs
