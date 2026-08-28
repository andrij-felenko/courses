from typing import Dict

class GCounter:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.state: Dict[str, int] = {}

    def increment(self, delta: int = 1) -> None:
        self.state[self.node_id] = self.state.get(self.node_id, 0) + delta

    @property
    def value(self) -> int:
        return sum(self.state.values())

    # Операція злиття над join-напіврешіткою: покомпонентний максимум
    def merge(self, other: "GCounter") -> None:
        all_nodes = set(self.state.keys()) | set(other.state.keys())
        for node in all_nodes:
            self.state[node] = max(self.state.get(node, 0), other.state.get(node, 0))
