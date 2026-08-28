from enum import Enum, auto

class WinKind(Enum):
    WIN_OK = auto()       # обидва краї вікна — справжні межі ока
    WIN_CLIP_LO = auto()  # вікно впирається у код 0 — око тягнеться нижче діапазону
    WIN_CLIP_HI = auto()  # вікно впирається у range_max-1 — око тягнеться вище
    WIN_NONE = auto()     # вікна нема (усе F)

def classify(w: Window, n: int) -> WinKind:
    if w.width == 0:       return WinKind.WIN_NONE
    if w.lo == 0:          return WinKind.WIN_CLIP_LO   # почалось на самому краю
    if w.hi == n - 1:      return WinKind.WIN_CLIP_HI   # дійшло до самого краю
    return WinKind.WIN_OK
