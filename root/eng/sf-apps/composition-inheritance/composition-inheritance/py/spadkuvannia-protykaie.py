# Було: контракт протікає — успадкували ВЕСЬ список
class Stack(list):                        # s[2], s.insert(...) — усе відкрито
    def push(self, x): self.append(x)
    def pop_top(self): return self.pop()

# Стало: список СХОВАНО полем, назовні лише push/pop
class Stack:
    def __init__(self):
        self._data = []                   # приватне — клієнт його не бачить
    def push(self, x): self._data.append(x)
    def pop(self): return self._data.pop()
    def empty(self): return not self._data
