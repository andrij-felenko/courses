  private trim(): void {
    while (this.bytes > this.budget && this.steps.length > 1 && this.index > 0) {
      const dead = this.steps.shift()!;   // O(n) на масиві: для десятків тисяч кроків
      this.bytes -= dead.weight;          // беруть кільцевий буфер або зсув-основу
      this.index--;
      if (this.saved >= 0) this.saved = this.saved > 0 ? this.saved - 1 : -1;
      this.retire(dead, "bottom");
    }
  }

  // Пам'ять звільнить збирач сміття — сам і колись. Але жодного деструктора він не викличе:
  // URL.revokeObjectURL, texture.delete(), закриття файлу — це доводиться робити руками.
  // Тому крок і носить два списки: з дна помирає ВИЛУЧЕНЕ ним, зі зрізу — ДОДАНЕ ним.
  private retire(dead: Step, end: "bottom" | "top"): void {
    for (const n of end === "bottom" ? dead.dropped : dead.added) n.res?.release();
  }
