from typing import NamedTuple, Sequence

class StreamStats(NamedTuple):
    max: int          # крайні значення
    min: int
    imax: int         # індекси відліків, де вони сталися
    imin: int
    range: int        # розмах max − min (peak-to-peak)

def scan_stream(x: Sequence[int]) -> StreamStats:
    mx = mn = x[0]    # ПОЧАТОК — з першого відліку, не з 0 і не з 0xFFFF
    imx = imn = 0
    for i in range(1, len(x)):
        if x[i] > mx:            # «A > B» на максимум
            mx, imx = x[i], i
        elif x[i] < mn:          # «A < B» на мінімум
            mn, imn = x[i], i
    return StreamStats(mx, mn, imx, imn, mx - mn)
