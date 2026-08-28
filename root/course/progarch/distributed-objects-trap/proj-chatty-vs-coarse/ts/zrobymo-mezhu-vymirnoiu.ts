// Перехід через межу невидимий у коді — тому й пастка.
// Зробимо його ВИМІРНИМ: кожен перехід іде крізь Link, і той його лічить.
class Link {
  crossings = 0;
  // один похід туди-й-назад; реального дроту нема — є облік дотиків до нього
  async cross<T>(work: () => T): Promise<T> {
    this.crossings++;
    return work();                 // тут «летіли б байти»; ми лише рахуємо перехід
  }
  costMs(perCrossing: number): number {
    return this.crossings * perCrossing;   // 0.5 — той самий ДЦ; 150 — через океан
  }
}
