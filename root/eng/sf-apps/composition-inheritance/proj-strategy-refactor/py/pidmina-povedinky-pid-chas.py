class Enemy:
    def __init__(self, weapon, armor):
        self.weapon = weapon
        self.armor  = armor

    def attack(self): return self.weapon.hit()
    def defend(self): return self.armor.block()

    # Підміна стратегії НА ЛЬОТУ — той самий об'єкт, інша поведінка.
    def rearm(self, w): self.weapon = w

foe = Enemy(Sword(), Heavy())
print(f"до: атака {foe.attack()}")      # до: атака 10

foe.rearm(Bow())                        # меч зламався — беремо лук
print(f"після: атака {foe.attack()}")   # після: атака 6
