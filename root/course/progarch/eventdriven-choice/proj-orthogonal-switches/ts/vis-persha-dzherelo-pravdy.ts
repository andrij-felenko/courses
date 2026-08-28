// ── Вісь 1: ДЖЕРЕЛО ПРАВДИ ──
interface Truth {
  handle(cmd: Command): DoorEvent;   // виконати команду, повернути факт
  state(): LockState;                // поточний стан замка
}

// ВИМК — CRUD: одна клітинка, перезапис; минуле стерто
class CrudTruth implements Truth {
  private s: LockState = INITIAL;
  handle(cmd: Command): DoorEvent {
    const e = decide(this.s, cmd);
    this.s = apply(this.s, e);        // ← стан перезаписано, що було — забуто
    return e;
  }
  state(): LockState { return this.s; }
}

// УВІМК — event sourcing: append-only журнал; стан = згортка журналу
class EventTruth implements Truth {
  private log: DoorEvent[] = [];
  handle(cmd: Command): DoorEvent {
    const e = decide(this.state(), cmd);
    this.log.push(e);                 // ← лише дописуємо; нічого не стираємо
    return e;
  }
  state(): LockState { return this.log.reduce(apply, INITIAL); }  // згортка щоразу
}
