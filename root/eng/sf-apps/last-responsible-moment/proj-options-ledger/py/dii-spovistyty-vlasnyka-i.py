@dataclass
class AdrSupersede:
    supersedes: str
    rationale: str
    status: str = "proposed"

def notify(owner: str, message: str) -> None:
    ...   # межа інтеграції: канал команди (чат, пошта, тикет)

def act(ev: FireEvent, roster: set[str], fallback: str) -> AdrSupersede:
    # Пастка «осиротілий власник»: перевіряємо, що власник іще живий.
    owner = ev.owner if ev.owner in roster else fallback
    orphaned = owner != ev.owner

    lines = [
        f"Настав відповідальний момент: {ev.title}.",
        f"Невизначеність знято — час обрати з: {', '.join(ev.options)}.",
    ]
    if orphaned:
        lines.append(f"⚠ Власник {ev.owner!r} поза командою — ескальовано на {owner}.")
    notify(owner, " ".join(lines))

    return AdrSupersede(supersedes=ev.adr,
                        rationale=f"Тригер спрацював: {ev.uncertainty}.")
