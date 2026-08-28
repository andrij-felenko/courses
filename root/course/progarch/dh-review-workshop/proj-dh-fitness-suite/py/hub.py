# hub.py — обробіток команд ідемпотентний за command-id
from dataclasses import dataclass

@dataclass(frozen=True)
class Command:
    id: str
    target: str
    action: str

class Lock:
    def __init__(self, target):
        self.target = target
        self.actuations = 0            # скільки разів фізично смикнули замок
    def actuate(self):
        self.actuations += 1

class Hub:
    def __init__(self):
        self._locks = {}
        self._seen = set()             # command-id, уже застосовані
    def lock(self, target):
        return self._locks.setdefault(target, Lock(target))
    def handle(self, cmd):
        if cmd.id in self._seen:       # дубль: той самий id — стан не рухаємо
            return
        self._seen.add(cmd.id)
        if cmd.action == "open":
            self.lock(cmd.target).actuate()
