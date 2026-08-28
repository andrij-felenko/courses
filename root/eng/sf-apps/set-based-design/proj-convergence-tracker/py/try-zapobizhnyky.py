# ── Запобіжник 1: перетягнуте обмеження ──────────────────────────────
class OverConstrained(Exception):
    def __init__(self, fact: Fact, wiped: list[str]):
        self.fact, self.wiped = fact, wiped
        super().__init__(
            "факт «%s» не лишає живим НІКОГО (стирає: %s). Це не збіжність, а "
            "порожній перетин: або обмеження перетягнуте, або в наборі бракує "
            "кандидата. Розширюй набір чи послаблюй межу — але свідомо й у журналі."
            % (fact.says, ", ".join(wiped)))

def land(journal: list[Event], fact: Fact) -> list[Event]:
    st = replay(journal, upto=fact.when)      # стан СТАНОМ НА дату факта
    if st.alive and not any(fact.holds(o) for o in st.alive):
        raise OverConstrained(fact, [o.name for o in st.alive])
    return journal + [Learned(fact)]          # журнал лише доростає з хвоста

# ── Запобіжник 2: вибуття, що тримається лише на здогаді ─────────────
def provisional(st: State) -> list[str]:
    return sorted(name for name, killers in st.killed_by.items()
                  if not any(f.evidence in PROVEN for f in killers))

# ── Присуд: єдине, заради чого все це будувалося ─────────────────────
OVERCONSTRAINED, NARROWING, STUCK, FAKE, CONVERGED = (
    "ПОРОЖНЬО", "ЗВУЖУЄМО", "ЗАСТРЯГЛО", "УДАВАНА ЗБІЖНІСТЬ", "ЗБІГЛОСЯ")

def verdict(st: State, today: date, deadline: date) -> tuple[str, str]:
    if not st.alive:
        return OVERCONSTRAINED, "живих не лишилось — перетин порожній"
    unproven = provisional(st)
    if len(st.alive) == 1:
        if unproven:
            return FAKE, ("живий один (%s), але вибуття %s тримається лише на "
                          "здогаді — доведи факт або поверни варіант у набір"
                          % (st.alive[0].name, ", ".join(unproven)))
        return CONVERGED, ("живий один (%s), кожне вибуття доведене — фіксуй"
                           % st.alive[0].name)
    names = ", ".join(o.name for o in st.alive)
    left = (deadline - today).days
    if left <= 0:
        return STUCK, ("живих ще %d (%s), а дедлайн збіжності минув %d дн. тому: "
                       "задарма фактів більше не буде — обирай зараз"
                       % (len(st.alive), names, -left))
    return NARROWING, ("живих %d (%s); до дедлайну %d дн. — який факт уб'є котрого?"
                       % (len(st.alive), names, left))

# ── Відповідь на питання «чому не взяли…» ────────────────────────────
def explain(st: State, name: str) -> str:
    killers = st.killed_by.get(name)
    if killers is None:
        return "%s — живий" % name
    return "\n".join("%s ✗ %s   [%s · %s · %s · %s]"
                     % (name, f.says, f.id, f.evidence, f.source, f.when)
                     for f in killers)
