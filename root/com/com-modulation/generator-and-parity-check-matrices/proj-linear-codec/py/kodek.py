from collections import deque


def bits(s: str) -> int:
    """Рядок матриці, ЯК НАДРУКОВАНО, зліва направо ("110") → маска: позиція i ↔ біт i.
    Уся домовленість про порядок бітів живе тут і більше ніде."""
    return sum(1 << i for i, ch in enumerate(s) if ch == "1")


class LinearCode:
    def __init__(self, n: int, k: int, P: list[int]):
        """P — k рядків по (n−k) бітів; більше про код знати нічого не треба."""
        self.n, self.k = n, k
        self.g = [(1 << j) | (P[j] << k) for j in range(k)]                # G = [ I | P ]
        self.hcol = [P[j] if j < k else 1 << (j - k) for j in range(n)]    # стовпці H = [ Pᵀ | I ]
        self.hrow = [sum(((P[j] >> i) & 1) << j for j in range(k)) | (1 << (k + i))
                     for i in range(n - k)]                                # рядки H
        self.table = self._leaders()

    @staticmethod
    def _xor_selected(masks: list[int], selector: int) -> int:
        """Єдиний примітив: XOR тих масок, проти яких у селекторі стоїть одиниця."""
        acc = 0
        for i, mask in enumerate(masks):
            if selector >> i & 1:
                acc ^= mask
        return acc

    def encode(self, m: int) -> int:
        return self._xor_selected(self.g, m)

    def syndrome(self, r: int) -> int:
        return self._xor_selected(self.hcol, r)

    def syndrome_by_rows(self, r: int) -> int:
        """Той самий синдром «по рядках»: n−k згорток замість n проходів."""
        return sum(((row & r).bit_count() & 1) << i for i, row in enumerate(self.hrow))

    def _leaders(self) -> list[int]:
        """Лідери суміжних класів = найкоротші шляхи від нульового синдрому."""
        table = [None] * (1 << (self.n - self.k))
        table[0] = 0
        q = deque([0])
        while q:
            s = q.popleft()
            for j, col in enumerate(self.hcol):
                s2 = s ^ col
                if table[s2] is None:            # перший, хто дійшов, — найлегший
                    table[s2] = table[s] ^ (1 << j)
                    q.append(s2)
        return table

    def decode(self, r: int) -> tuple[int, int]:
        e = self.table[self.syndrome(r)]     # table[0] == 0 → чисте слово лишиться цілим
        c = r ^ e
        return c & ((1 << self.k) - 1), e    # систематичність: дані — нижні k бітів
