class Monster {
  constructor(
    public name: string,
    public hp: number,
    public stats: Stats,
    public loot: string[],
    public speed = 1,          // ← ДОДАЛИ пізніше
  ) {}

  clone(): Monster {
    // забули про speed! кожен клон тихо дістане speed = 1
    return new Monster(this.name, this.hp, this.stats.clone(), [...this.loot]);
  }
}
