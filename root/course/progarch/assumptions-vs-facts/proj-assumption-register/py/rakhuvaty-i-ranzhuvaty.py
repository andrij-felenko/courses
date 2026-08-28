def load(path: str) -> list[Assumption]:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    reg = [Assumption(state=State(r.pop("state")), **r) for r in raw]
    for a in reg:
        if not 0.0 <= a.p_wrong <= 1.0:
            raise ValueError(f"{a.id}: P поза [0,1] — {a.p_wrong}")
        if a.loss < 0 or a.cost_to_check < 0:
            raise ValueError(f"{a.id}: відʼємна ціна")
    return reg


def ranked(reg: list[Assumption]) -> list[Assumption]:
    live = [a for a in reg if a.state in LIVE]
    return sorted(live, key=lambda a: a.expected_loss(), reverse=True)


def check_first(reg: list[Assumption]) -> list[Assumption]:
    return [a for a in ranked(reg) if a.worth_checking()]


def report(reg: list[Assumption]) -> None:
    print("що перевіряти першим (спадання очікуваної втрати):")
    for i, a in enumerate(check_first(reg), 1):
        flag = "  ⟵ ГЕЙТ незворотного кроку" if a.irreversible else ""
        print(f"{i:>2}. {a.expected_loss():5.1f}  {a.claim}{flag}")
    watch = [a for a in reg if a.state is State.ACCEPTED]
    if watch:
        print("\nпід сигнальним знаком (стежити, не перевіряти):")
        for a in watch:
            print(f"  • {a.claim} → знак: {a.signpost}")
