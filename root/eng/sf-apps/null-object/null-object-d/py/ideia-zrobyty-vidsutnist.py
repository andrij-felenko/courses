from typing import Protocol

class Logger(Protocol):
    def write(self, msg: str) -> None: ...

class FileLogger:
    def __init__(self, path: str) -> None:
        self._path = path
    def write(self, msg: str) -> None:
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

class NullLogger:
    def write(self, msg: str) -> None:
        pass                        # навмисно нічого
