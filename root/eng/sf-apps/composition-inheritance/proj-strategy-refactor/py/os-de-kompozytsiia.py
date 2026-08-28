# Нова вісь — новий інтерфейс + по одному класу на вид. І ВСЕ.
class Element:
    def bonus(self): ...   # додаткова шкода від стихії
    def name(self):  ...
class Plain(Element):
    def bonus(self): return 0
    def name(self):  return "звичайна"
class Fire(Element):
    def bonus(self): return 4
    def name(self):  return "вогонь"
class Ice(Element):
    def bonus(self): return 3
    def name(self):  return "крига"
