# Лічимо зриви FLT у ковзному вікні; якщо їх забагато — аварія стійка.
_fault_hits = 0
_prev_fault = False
_window     = 0

# Кличемо, приміром, кожні 10 мс із таймера.
def efuse_persistent_fault():
    global _fault_hits, _prev_fault, _window
    now = efuse_fault()
    if now and not _prev_fault:
        _fault_hits += 1                    # рахуємо ФРОНТ у зрив, не рівень
    _prev_fault = now

    # за 3 с (300 викликів по 10 мс) більш ніж 5 зривів — стійка аварія
    _window += 1
    if _window >= 300:
        persistent = _fault_hits > 5
        _window = 0                         # почати нове вікно
        _fault_hits = 0
        return persistent
    return False
