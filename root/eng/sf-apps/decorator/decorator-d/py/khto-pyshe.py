class Forwarder:
    """переспрямовує будь-який невизначений атрибут на inner —
       базового делегування писати не треба взагалі."""
    def __init__(self, inner): self._inner = inner
    def __getattr__(self, name):
        return getattr(self._inner, name)   # усе, чого нема тут, — вниз, автоматично

class LoudList(Forwarder):
    def append(self, x):                    # єдине, що змінюємо
        print("append", x)
        return self._inner.append(x)

xs = LoudList([1, 2, 3])
xs.append(4)     # надрукує "append 4", тоді делегує
xs.index(2)      # index() тут нема → __getattr__ → list.index, повертає 1
