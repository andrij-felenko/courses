SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}


def skipped(path: Path) -> bool:
    return any(part in SKIP for part in path.parts)


def refs_in_comments(path: Path) -> set[int]:
    """ADR-номери з КОМЕНТАРІВ .py — не з рядків-літералів (ось де ховалася пастка)."""
    nums: set[int] = set()
    try:
        with tokenize.open(path) as f:                # враховує coding-cookie файлу
            for tok in tokenize.generate_tokens(f.readline):
                if tok.type == tokenize.COMMENT:      # рядок-літерал сюди не потрапить
                    nums |= {int(n) for n in ID_RE.findall(tok.string)}
    except (tokenize.TokenError, SyntaxError, ValueError):
        pass                                          # битий синтаксис не валить перевірку сліду
    return nums


def strip_front_matter(text: str) -> str:
    """Прибрати YAML-шапку: її поля читає ланцюг замін, це не «згадки» в прозі."""
    return re.sub(r"^---\r?\n.*?\r?\n---\r?\n", "", text, count=1, flags=re.S)


def refs_in_prose(path: Path) -> set[int]:
    """ADR-номери з тексту діаграм і markdown (без структурного фронт-матера)."""
    body = strip_front_matter(path.read_text(encoding="utf-8", errors="ignore"))
    return {int(n) for n in ID_RE.findall(body)}


@dataclass
class Break:
    adr: str        # ім'я винного запису — саме воно потрапить у лог CI
    detail: str


def check_dangling_refs(adrs: dict[int, Adr], repo: Path) -> list[Break]:
    known = set(adrs)                                 # множина наявних номерів
    out: list[Break] = []
    for path in sorted(repo.rglob("*")):
        if not path.is_file() or skipped(path):
            continue
        if path.suffix == ".py":
            found = refs_in_comments(path)
        elif path.suffix in (".md", ".puml", ".svg", ".dot"):
            found = refs_in_prose(path)
        else:
            continue
        for num in sorted(found - known):             # згадано, а запису нема
            out.append(Break(canon(num),
                f"згадано у {path.as_posix()}, а запису в {ADR_DIR.as_posix()} нема"))
    return out
