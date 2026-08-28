class PNCounter:
    def __init__(self, node_id: str):
        self.p_counter = GCounter(node_id)
        self.n_counter = GCounter(node_id)

    def increment(self, delta: int = 1) -> None:
        self.p_counter.increment(delta)

    def decrement(self, delta: int = 1) -> None:
        self.n_counter.increment(delta)

    @property
    def value(self) -> int:
        return self.p_counter.value - self.n_counter.value

    def merge(self, other: "PNCounter") -> None:
        self.p_counter.merge(other.p_counter)
        self.n_counter.merge(other.n_counter)
