class Line:
    def at(self, i: int) -> str: ...
    def render(self) -> str: ...

# КОНКРЕТНИЙ КОМПОНЕНТ: render() будує все ЧЕРЕЗ at()
class Plain(Line):
    def __init__(self, s: str): self._s = s
    def at(self, i): return self._s[i]
    def render(self):
        return "".join(self.at(i) for i in range(len(self._s)))  # self.at(i)!

# БАЗОВИЙ ДЕКОРАТОР — делегує все
class LineDecorator(Line):
    def __init__(self, inner: Line): self._inner = inner
    def at(self, i):   return self._inner.at(i)
    def render(self):  return self._inner.render()   # просто делегує

# КОНКРЕТНИЙ ДЕКОРАТОР: кожен символ — великим
class Upper(LineDecorator):
    def at(self, i): return self._inner.at(i).upper()
    # render() навмисно не чіпаємо

x = Upper(Plain("abc"))
x.at(0)      # 'A'   — decorate спрацював
x.render()   # 'abc' — decorate ОБІЙДЕНО, малі літери!
