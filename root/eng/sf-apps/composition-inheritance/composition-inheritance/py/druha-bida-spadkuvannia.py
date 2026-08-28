# Кожна вісь — окремий інтерфейс поведінки
class Weapon: 
    def hit(self):   ...   # скільки шкоди завдає
class Armor:  
    def block(self): ...   # скільки шкоди тримає

class Sword(Weapon): 
    def hit(self):   return 10
class Bow(Weapon):   
    def hit(self):   return 6
class Light(Armor):  
    def block(self): return 2
class Heavy(Armor):  
    def block(self): return 7

# Ворог НЕ успадковує зброю чи броню — він їх ТРИМАЄ
class Enemy:
    def __init__(self, weapon, armor):
        self.weapon = weapon
        self.armor  = armor
    def attack(self): return self.weapon.hit()
    def defend(self): return self.armor.block()

# Будь-яку комбінацію збирають на місці — нового класу не треба
archer = Enemy(Bow(), Heavy())
