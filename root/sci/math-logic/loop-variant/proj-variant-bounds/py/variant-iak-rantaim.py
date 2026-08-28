class Variant:
    """Строгий спад + дно + збіг із передбаченою межею."""

    def __init__(self, floor=0, budget=None):
        self.floor, self.budget = floor, budget
        self.prev, self.steps = None, 0

    def step(self, now):
        """Викликати ПЕРШИМ рядком тіла циклу — жодна гілка не прослизне."""
        self.steps += 1
        assert now >= self.floor, "варіант пробив дно: %r < %r" % (now, self.floor)
        if self.prev is not None:
            assert now < self.prev, "варіант не впав: %r → %r" % (self.prev, now)
        if self.budget is not None:
            assert self.steps <= self.budget, \
                "перевищено передбачену межу: %d > %d" % (self.steps, self.budget)
        self.prev = now
