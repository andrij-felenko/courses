// 1. Спільний інтерфейс поведінки (роль «Стратегія»)
interface AttackStrategy {
  attack(): number;
}

// 2. Конкретні стратегії — взаємозамінні реалізації
class SwordAttack implements AttackStrategy {
  attack(): number { return 10; }
}
class BowAttack implements AttackStrategy {
  attack(): number { return 6; }
}

// 3. Власник ТРИМАЄ стратегію полем і делегує їй, не знаючи, яка саме
class Enemy {
  constructor(private strategy: AttackStrategy) {}
  setStrategy(s: AttackStrategy): void { this.strategy = s; } // підміна на льоту
  hit(): number { return this.strategy.attack(); }
}

const goblin = new Enemy(new SwordAttack());
console.log(goblin.hit());          // 10
goblin.setStrategy(new BowAttack());
console.log(goblin.hit());          // 6 — поведінка змінилась, ворога не переписували
