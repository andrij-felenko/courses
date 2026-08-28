from typing import Callable, Generic, TypeVar
import threading

T = TypeVar("T")

class Observer(Generic[T]):
    def next(self, value: T) -> None: ...
    def complete(self) -> None: ...
    def error(self, e: object) -> None: ...

# потік = функція, що приймає спостерігача й починає його годувати,
# і повертає «відписку»
Stream = Callable[[Observer[T]], Callable[[], None]]

def interval(seconds: float) -> Stream:
    def start(observer: Observer) -> Callable[[], None]:
        n = 0
        stopped = threading.Event()
        def tick() -> None:
            nonlocal n
            if stopped.is_set():
                return
            observer.next(n)
            n += 1
            threading.Timer(seconds, tick).start()
        threading.Timer(seconds, tick).start()
        return stopped.set   # виклич, щоб зупинити потік
    return start
