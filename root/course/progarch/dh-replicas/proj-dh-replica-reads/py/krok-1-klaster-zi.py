class Rng:                                    # детермінований ГВЧ (LCG)
    def __init__(self, seed): self.s = seed & 0xFFFFFFFF
    def next(self):
        self.s = (1664525 * self.s + 1013904223) & 0xFFFFFFFF
        return self.s / 4294967296
    def below(self, p): return self.next() < p
    def index(self, n): return int(self.next() * n)
    def pick(self, xs): return xs[int(self.next() * len(xs))]

class Clock:
    def __init__(self): self.t = 0.0
    def advance(self, dt): self.t += dt

class Leader:
    def __init__(self): self.state, self.log = {}, []
    def apply_write(self, home, device, value, t):
        seq = len(self.log)                   # монотонний номер запису
        self.state[(home, device)] = (value, seq)
        self.log.append((seq, t, home, device, value))
        return seq
    def get(self, home, device): return self.state.get((home, device))

class Follower:
    def __init__(self, leader, lag):
        self.leader, self.lag = leader, lag
        self.state, self.cursor = {}, 0
    def replicate(self, now):                 # доганяємо лідера до межі now − lag
        log = self.leader.log
        while self.cursor < len(log) and log[self.cursor][1] <= now - self.lag:
            seq, t, home, device, value = log[self.cursor]
            self.state[(home, device)] = (value, seq)
            self.cursor += 1
    def get(self, home, device): return self.state.get((home, device))

class Cluster:
    def __init__(self, lags):
        self.clock, self.leader = Clock(), Leader()
        self.followers = [Follower(self.leader, lag) for lag in lags]
    def tick(self, dt):
        self.clock.advance(dt)
        for fol in self.followers: fol.replicate(self.clock.t)
    def write(self, home, device, value):
        return self.leader.apply_write(home, device, value, self.clock.t)
