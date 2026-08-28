class Rect:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h

    def set_width(self, w: int) -> None:   # висоту НЕ чіпає
        self.w = w

    def set_height(self, h: int) -> None:
        self.h = h

    def area(self) -> int:
        return self.w * self.h
