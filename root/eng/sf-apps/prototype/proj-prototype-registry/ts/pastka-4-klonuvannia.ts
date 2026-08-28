class Monster {
  clone(): Monster {
    const c = Object.assign(Object.create(Monster.prototype), this);
    c.stats = this.stats.clone();
    c.loot = [...this.loot];
    // ЖИВІ ресурси — свідоме рішення на кожен:
    c.telemetry = this.telemetry;        // (а) ПОДІЛИТИ: спільна інфраструктура
    c.socket = null;                     // (б) СКИНУТИ: копія під'єднається сама, ліниво
    c.logFile = openLog(this.logPath);   // (в) ПЕРЕВІДКРИТИ: власний свіжий дескриптор
    return c;
  }
}
