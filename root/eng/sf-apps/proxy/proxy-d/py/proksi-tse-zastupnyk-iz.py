from typing import Protocol

class Image(Protocol):
    def draw(self) -> None: ...
    def width(self) -> int: ...

# Справжній об'єкт: створення = читання файлу з диска (дорого).
class RealImage:
    def __init__(self, path: str) -> None:
        self.pixels = load_from_disk(path)     # читаємо ВЕСЬ файл уже в конструкторі
        print(f"завантажено {path}")

    def draw(self) -> None:
        ...   # малюємо pixels

    def width(self) -> int:
        return read_width_of(self.pixels)
