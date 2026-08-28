class ReadRouter:
    def __init__(self, cluster, lag_window=1.5,
                 classify=True, sticky=True, pin=True, rng=None):
        self.c, self.lag_window = cluster, lag_window
        self.classify, self.sticky, self.pin = classify, sticky, pin
        self.last_write, self.rng = {}, rng or Rng(7)

    def note_write(self, home):               # застосунок щойно писав у цей дім
        self.last_write[home] = self.c.clock.t

    def route(self, home, kind):
        if not self.classify:                 # наївний режим: усе на фоловери
            return self._follower(home)
        if kind == "lock":                    # безпека: замок завжди з лідера
            return self.c.leader
        if kind == "device_state" and self.sticky:
            if self.c.clock.t - self.last_write.get(home, -1e9) < self.lag_window:
                return self.c.leader          # read-your-writes: свій свіжий запис
        return self._follower(home)           # реєстр, телеметрія, давній стан

    def _follower(self, home):
        n = len(self.c.followers)
        # прив'язка: сесія (тут — дім) завжди на ТУ САМУ копію → монотонні читання
        return self.c.followers[home % n] if self.pin \
            else self.c.followers[self.rng.index(n)]
