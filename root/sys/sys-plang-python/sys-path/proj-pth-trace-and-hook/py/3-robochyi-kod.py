def attribute(replay: PthReplay) -> list[tuple[int, str, str]]:
    """Кожному елементу sys.path — рядок пояснення, звідки він узявся."""
    env = [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p]
    env_cases = {makepath(p)[1] for p in env}
    site_cases = {makepath(d)[1] for d in replay.sitedirs}
    prefixes = tuple(makepath(p)[1] for p in (sys.prefix, sys.base_prefix))

    rows: list[tuple[int, str, str]] = []
    for i, entry in enumerate(sys.path):
        if entry == "":
            rows.append((i, entry, "порожній рядок — поточний каталог процесу"))
            continue
        case = makepath(entry)[1]
        if case in site_cases:
            source = "каталог site-packages (додав site.addsitedir)"
        elif case in env_cases:
            source = "змінна оточення PYTHONPATH"
        elif case in replay.owner:
            line = replay.owner[case]
            source = f".pth → {line.where()}  «{line.raw.strip()}»"
        elif case.startswith(prefixes):
            source = "стандартна бібліотека (розрахунок префікса)"
        elif i == 0:
            source = "точка входу: каталог скрипту або cwd"
        else:
            source = "НЕВІДОМО — мутація під час виконання або рядок import у .pth"
        rows.append((i, entry, source))
    return rows


def main() -> int:
    sitedirs = list(site.getsitepackages())
    if site.ENABLE_USER_SITE:
        sitedirs.append(site.getusersitepackages())
    replay = PthReplay(sitedirs).run()

    print("=== sys.path з авторством ===")
    for i, entry, source in attribute(replay):
        print(f"[{i:2d}] {entry or '(порожньо)'}\n     ↳ {source}")

    execs = [ln for ln in replay.lines if ln.kind == "exec"]
    if execs:
        print("\n=== код, що виконався до вашої програми ===")
        for ln in execs:
            print(f"  {ln.where():40s} {ln.raw.strip()}")

    dead = [ln for ln in replay.lines
            if ln.kind == "path" and "нема на диску" in ln.note]
    if dead:
        print("\n=== мертві рядки (каталог зник) ===")
        for ln in dead:
            print(f"  {ln.where():40s} → {ln.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
