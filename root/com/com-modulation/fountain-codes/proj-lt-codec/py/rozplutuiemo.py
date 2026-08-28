class LTDecoder:
    def __init__(self, k, mu):
        self.k, self.mu = k, mu
        self.blocks = [None] * k                 # відновлені блоки
        self.recovered = 0
        self.contains = [[] for _ in range(k)]   # блок → краплі, що його містять

    def add(self, seed, payload):
        idx = set(droplet_recipe(seed, self.k, self.mu))
        val = bytearray(payload)
        for i in list(idx):                      # одразу вирізаємо вже відоме
            if self.blocks[i] is not None:
                xor_into(val, self.blocks[i])
                idx.discard(i)
        if not idx:
            return                               # надлишкова крапля — усе вже відомо
        drop = [idx, val]
        for i in idx:
            self.contains[i].append(drop)
        if len(idx) == 1:
            self._peel(drop)

    def _peel(self, drop):
        ripple = [drop]                          # черга крапель степеня 1
        while ripple:
            idx, val = ripple.pop()
            if len(idx) != 1:                    # степінь міг змінитись у черзі
                continue
            i = next(iter(idx))
            if self.blocks[i] is not None:
                continue
            self.blocks[i] = bytes(val)          # відкрили блок i
            self.recovered += 1
            for nb in self.contains[i]:          # виріж i з усіх його сусідів
                nb_idx, nb_val = nb
                if i in nb_idx:
                    xor_into(nb_val, self.blocks[i])
                    nb_idx.discard(i)
                    if len(nb_idx) == 1:
                        ripple.append(nb)
            self.contains[i] = []

    def done(self):
        return self.recovered == self.k

    def file(self):
        return b"".join(self.blocks)
