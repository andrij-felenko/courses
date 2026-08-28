# ── Вісь «зброя»: інтерфейс + різновиди (по одному класу на вид) ──
class Weapon:
    def hit(self):  ...   # скільки шкоди завдає
    def name(self): ...
class Sword(Weapon):
    def hit(self):  return 10        # логіка меча — В ОДНОМУ місці
    def name(self): return "меч"
class Bow(Weapon):
    def hit(self):  return 6
    def name(self): return "лук"

# ── Вісь «броня»: інтерфейс + різновиди ──
class Armor:
    def block(self): ...   # скільки шкоди тримає
    def name(self):  ...
class Light(Armor):
    def block(self): return 2
    def name(self):  return "легка"
class Heavy(Armor):
    def block(self): return 7
    def name(self):  return "важка"
class Magic(Armor):
    def block(self): return 5
    def name(self):  return "магічна"

# ── Ворог НЕ успадковує осі — він їх ТРИМАЄ полями ──
class Enemy:
    def __init__(self, weapon, armor):
        self.weapon = weapon        # яка зброя зараз
        self.armor  = armor         # яка броня зараз

    # Делегувальні обгортки: ворог не рахує сам, а перепитує деталь.
    def attack(self): return self.weapon.hit()
    def defend(self): return self.armor.block()

    def describe(self):
        print(f"ворог: {self.weapon.name()} + {self.armor.name()} → "
              f"атака {self.attack()}, захист {self.defend()}")
