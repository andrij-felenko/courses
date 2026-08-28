class PizzaBuilder:
    def __init__(self, size):            # обов'язкове поле — у конструкторі
        self._size = size
        self._cheese = False
        self._bacon = False

    def cheese(self):                    # крок повертає САМ будівельник...
        self._cheese = True
        return self                      # ...тому виклики й чіпляються в ланцюжок

    def bacon(self):
        self._bacon = True
        return self

    def build(self):                     # остаточне зібрання — тут
        return Pizza(self._size, self._cheese, self._bacon)
