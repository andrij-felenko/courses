import uuid
from typing import Set, Tuple

class ORSet:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.add_set: Set[Tuple[str, str]] = set()  # (value, tag)
        self.remove_set: Set[str] = set()           # tag

    def add(self, value: str) -> None:
        tag = f"{self.node_id}:{uuid.uuid4().hex}"
        self.add_set.add((value, tag))

    def remove(self, value: str) -> None:
        for val, tag in self.add_set:
            if val == value:
                self.remove_set.add(tag)

    def contains(self, value: str) -> bool:
        return any(val == value and tag not in self.remove_set for val, tag in self.add_set)

    def read(self) -> Set[str]:
        return {val for val, tag in self.add_set if tag not in self.remove_set}

    # Злиття над напіврешіткою: об'єднання множин (Union Semilattice)
    def merge(self, other: "ORSet") -> None:
        self.add_set |= other.add_set
        self.remove_set |= other.remove_set
