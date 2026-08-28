from abc import ABC, abstractmethod

# Базовий ворог: обіцяє два числа — завдану й поглинуту шкоду.
class Enemy(ABC):
    @abstractmethod
    def attack(self): ...   # скільки шкоди завдає
    @abstractmethod
    def defend(self): ...   # скільки шкоди тримає

# Кожна КОМБІНАЦІЯ зброя×броня — окремий клас.
class SwordLight(Enemy):
    def attack(self): return 10   # меч
    def defend(self): return 2    # легка
class SwordHeavy(Enemy):
    def attack(self): return 10   # меч
    def defend(self): return 7    # важка
class BowLight(Enemy):
    def attack(self): return 6    # лук
    def defend(self): return 2    # легка
class BowHeavy(Enemy):
    def attack(self): return 6    # лук
    def defend(self): return 7    # важка
