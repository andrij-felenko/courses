class Queue:
    def __init__(self):
        self._in = []          # сюди пхаємо (enqueue)
        self._out = []         # звідси знімаємо (dequeue / peek)

    def enqueue(self, x):
        self._in.append(x)     # просто на вершину вхідного

    def _transfer(self):
        # переливаємо ЛИШЕ коли вихідний порожній — інакше зламаємо порядок
        if not self._out:
            while self._in:
                self._out.append(self._in.pop())   # друге перевертання

    def dequeue(self):
        self._transfer()
        if not self._out:
            raise IndexError("черга порожня")
        return self._out.pop()

    def peek(self):
        self._transfer()       # peek теж мусить перелити, якщо вихідний порожній
        if not self._out:
            raise IndexError("черга порожня")
        return self._out[-1]

    def __len__(self):
        return len(self._in) + len(self._out)
