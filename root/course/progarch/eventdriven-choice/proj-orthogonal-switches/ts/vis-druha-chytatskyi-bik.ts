// читацька форма — рядок панелі; інша, ніж форма запису
type DashRow = { status: string; lastActor: string; unlockedToday: number };

// ── Вісь 2: ЧИТАЦЬКИЙ БІК ──
interface Read {
  notify(e: DoorEvent): void;         // як читання дізнається про зміну
  dashboard(truth: Truth): DashRow;   // читацька відповідь
}

// ВИМК — та сама модель: рахуємо форму з правди на кожному читанні
class FoldOnRead implements Read {
  notify(_e: DoorEvent): void { /* нічого не тримаємо */ }
  dashboard(truth: Truth): DashRow {
    const s = truth.state();
    return {
      status: s.locked ? "ЗАЧИНЕНО" : "ВІДЧИНЕНО",
      lastActor: s.lastActor ?? "—",
      unlockedToday: -1,              // ← без історії підсумку не порахувати
    };
  }
}

// УВІМК — окрема проєкція (CQRS): тримаємо готовий рядок, оновлюємо подіями
class Projection implements Read {
  private row: DashRow = { status: "ВІДЧИНЕНО", lastActor: "—", unlockedToday: 0 };
  notify(e: DoorEvent): void {
    this.row.status    = e.type === "DoorLocked" ? "ЗАЧИНЕНО" : "ВІДЧИНЕНО";
    this.row.lastActor = e.actor;
    if (e.type === "DoorUnlocked") this.row.unlockedToday += 1;   // підсумок
  }
  dashboard(_truth: Truth): DashRow { return this.row; }  // готове, без обчислень
}
