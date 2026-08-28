from collections import deque


class ConvInterleaver:
    """Перемішувач Форні: N гілок, гілка i — лінія затримки на i·M комірок."""
    def __init__(self, N: int, M: int):
        self.N = N
        self.br = [deque([None] * (i * M)) for i in range(N)]   # гілки-кільця
        self.j = 0                                              # комутатор

    def push(self, s):
        i, self.j = self.j, (self.j + 1) % self.N
        if not self.br[i]:                     # гілка 0 порожня — наскрізь
            return s
        self.br[i].append(s)                   # новий у хвіст
        return self.br[i].popleft()            # найстаріший у канал


class ConvDeinterleaver(ConvInterleaver):
    """Дзеркало: гілка i затримує на (N−1−i)·M — сума з перемішувачем стала."""
    def __init__(self, N: int, M: int):
        super().__init__(N, M)
        self.br = [deque([None] * ((N - 1 - i) * M)) for i in range(N)]
