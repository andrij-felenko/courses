# ВИМК — CRUD: зберігаємо ПОТОЧНИЙ стан, перезаписуючи клітинку
def lock_door(lock_id):
    db.update("locks", lock_id, state="locked", at=now())
    # те, що було до цього, стерто назавжди: лишилось саме «зачинено»

# ───────────────── або ту саму дію інакше ─────────────────

# УВІМК — event sourcing: зберігаємо ФАКТ, дописуючи в журнал
def lock_door_sourced(lock_id):
    log.append(lock_id, {"type": "DoorLocked", "at": now()})
    # поточний стан нікуди не пишемо — його РАХУЮТЬ згорткою журналу:

def current_state(events):
    return reduce(apply, events, INITIAL_LOCK_STATE)  # згортка всієї історії
