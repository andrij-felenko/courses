from typing import Dict

class LWWSet:
    def __init__(self):
        # value -> [add_time, remove_time]
        self.elements: Dict[str, list] = {}

    def add(self, value: str, timestamp: int) -> None:
        if value not in self.elements:
            self.elements[value] = [0, 0]
        self.elements[value][0] = max(self.elements[value][0], timestamp)

    def remove(self, value: str, timestamp: int) -> None:
        if value not in self.elements:
            self.elements[value] = [0, 0]
        self.elements[value][1] = max(self.elements[value][1], timestamp)

    def contains(self, value: str) -> bool:
        if value not in self.elements:
            return False
        add_time, rem_time = self.elements[value]
        return add_time > rem_time

    # Злиття над join-напіврешіткою: покомпонентний максимум міток часу
    def merge(self, other: "LWWSet") -> None:
        all_keys = set(self.elements.keys()) | set(other.elements.keys())
        for k in all_keys:
            self_add, self_rem = self.elements.get(k, [0, 0])
            oth_add, oth_rem = other.elements.get(k, [0, 0])
            self.elements[k] = [max(self_add, oth_add), max(self_rem, oth_rem)]
