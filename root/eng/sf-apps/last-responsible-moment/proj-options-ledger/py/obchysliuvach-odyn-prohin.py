@dataclass
class FireEvent:
    decision_id: str
    title: str
    owner: str
    adr: str
    options: list[str]
    uncertainty: str

def tick(ledger: list[Decision], w: Window) -> list[FireEvent]:
    fired: list[FireEvent] = []
    for d in ledger:
        if d.status is Status.SUPERSEDED:            # закрите не чіпаємо
            continue
        armed = is_armed(d.trigger, w)
        firing = armed and is_firing(d.trigger, w)   # стріляти лише в межах смуги

        if d.status is Status.OPEN and armed:
            d.status = Status.ARMED
            d.hold_count = 0
        if d.status is Status.ARMED:
            if not armed:
                d.status = Status.OPEN               # відбій — тремтіння згашене
                d.hold_count = 0
            elif firing:
                d.hold_count += 1                    # стійкість: виміри поспіль
                if d.hold_count >= d.trigger.hold_for:
                    d.status = Status.DUE
                    fired.append(FireEvent(
                        d.id, d.title, d.owner, d.adr, d.options, d.uncertainty))
            else:
                d.hold_count = 0                     # серія урвалась
    return fired
