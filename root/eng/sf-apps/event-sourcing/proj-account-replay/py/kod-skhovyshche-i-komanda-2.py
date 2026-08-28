@dataclass(frozen=True)
class Account:
    balance: float = 0.0

EMPTY = Account()

# apply — СЛІПА: приймає народжену подію на віру, правил не знає.
def apply(state: Account, e) -> Account:
    if isinstance(e, Deposited):  return Account(state.balance + e.amount)
    if isinstance(e, Withdrawn):  return Account(state.balance - e.amount)
    if isinstance(e, FeeCharged): return Account(state.balance - e.amount)
    raise ValueError(f"невідома подія: {e!r}")

# Згорнути список збережених подій у стан.
def fold_state(events: list[Stored]) -> Account:
    state = EMPTY
    for st in events:
        state = apply(state, st.event)
    return state

# Команда «зняти»: правила ТУТ. Повертаємо, чи вдалося (для повтору при конфлікті).
def withdraw(store: EventStore, stream_id: str, amount: float) -> bool:
    history = store.read(stream_id)
    state = fold_state(history)                  # стан, на якому будуємо рішення
    expected_version = len(history)              # версія, яку ми бачили

    if amount <= 0:
        raise ValueError("сума має бути додатна")
    if amount > state.balance:
        return False                             # ПРАВИЛО: не даємо піти в мінус

    try:
        store.append(stream_id, expected_version, [Withdrawn(amount)])
        return True
    except VersionConflict:
        return False                             # хтось випередив — хай виклик повторить
