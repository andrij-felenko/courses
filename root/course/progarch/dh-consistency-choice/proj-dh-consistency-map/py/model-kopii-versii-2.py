class Cluster:
    def __init__(self, replicas, leader, lag):
        self.replicas, self.leader, self.lag = replicas, leader, lag
        self.clock = 0
        self.queue = []                    # (тик_доставки, копія, ключ, запис)
        self._next = 1                     # наступна версія

    def now(self) -> int:
        return self.clock

    # Запис через лідера: карбує версію, кладе В СЕБЕ негайно, на репліки — з лагом.
    def write(self, key: str, value: Any) -> int:
        rec = Rec(value, self._next); self._next += 1
        self.leader.apply(key, rec)
        for to in self.replicas:
            if to is self.leader:
                continue
            self.queue.append((self.clock + self.lag(to), to, key, rec))
        return rec.version

    # Просунути час і доставити дозрілі реплікації — лише копіям на зв'язку.
    # Відрізаній копії кадр лишається в черзі (майбутня робота анти-ентропії).
    def advance(self, ticks: int) -> None:
        self.clock += ticks
        kept = []
        for at, to, key, rec in self.queue:
            if at <= self.clock and to.linked:
                to.apply(key, rec)
            else:
                kept.append((at, to, key, rec))
        self.queue = kept
