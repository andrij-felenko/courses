// ВИМК — CRUD: зберігаємо ПОТОЧНИЙ стан, перезаписуючи клітинку
async function lockDoor(id: string) {
  await db.update("locks", id, { state: "locked", at: now() });
  // те, що було до цього, стерто назавжди: лишилось саме «зачинено»
}

// ───────────────── або ту саму дію інакше ─────────────────

// УВІМК — event sourcing: зберігаємо ФАКТ, дописуючи в журнал
async function lockDoorSourced(id: string) {
  await log.append(id, { type: "DoorLocked", at: now() });
  // поточний стан нікуди не пишемо — його РАХУЮТЬ згорткою журналу:
}
function currentState(events: Event[]): LockState {
  return events.reduce(apply, initialLockState);  // згортка всієї історії
}
