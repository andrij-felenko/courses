# 1. Спільний інтерфейс поведінки (роль «Стратегія»)
class AttackStrategy:
    def attack(self) -> int: ...

# 2. Конкретні стратегії — взаємозамінні реалізації
class SwordAttack(AttackStrategy):
    def attack(self) -> int: return 10

class BowAttack(AttackStrategy):
    def attack(self) -> int: return 6

# 3. Власник ТРИМАЄ стратегію полем і делегує їй, не знаючи, яка саме
class Enemy:
    def __init__(self, strategy: AttackStrategy):
        self._attack = strategy
    def set_strategy(self, strategy: AttackStrategy):  # підміна на льоту
        self._attack = strategy
    def hit(self) -> int:
        return self._attack.attack()

goblin = Enemy(SwordAttack())
print(goblin.hit())          # 10
goblin.set_strategy(BowAttack())
print(goblin.hit())          # 6 — поведінка змінилась, ворога не переписували
