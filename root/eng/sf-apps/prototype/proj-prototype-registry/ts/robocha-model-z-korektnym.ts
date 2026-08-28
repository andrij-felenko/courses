class Stats {
  constructor(
    public attack: number,
    public defense: number,
    public resist: Map<string, number>,   // вкладена ЗМІННА мапа опорів
  ) {}

  clone(): Stats {
    // глибоко: власна нова мапа, а не спільна з оригіналом
    return new Stats(this.attack, this.defense, new Map(this.resist));
  }
}

class Monster {
  constructor(
    public name: string,
    public hp: number,
    public stats: Stats,       // вкладений об'єкт
    public loot: string[],     // вкладений список
  ) {}

  clone(): Monster {
    return new Monster(
      this.name,               // рядок незмінний — просто значення
      this.hp,                 // число — просто значення
      this.stats.clone(),      // глибоко: власний Stats
      [...this.loot],          // глибоко: власний масив (елементи-рядки незмінні)
    );
  }
}
