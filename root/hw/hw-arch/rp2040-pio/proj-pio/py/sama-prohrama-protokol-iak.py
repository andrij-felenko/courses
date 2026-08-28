# WS2812 — rp2.asm_pio; clock divider → автомат на 20 МГц, 1 такт ≈ 50 нс
# один біт = 25 тактів ≈ 1.25 мкс
import rp2
from rp2 import PIO

@rp2.asm_pio(sideset_init=PIO.OUT_LOW,
             out_shiftdir=PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    wrap_target()
    label("bitloop")
    out(x, 1)             .side(0) [6]   # зсунути 1 біт у X; ніжка LOW  (7 тактів = 350 нс)
    jmp(not_x, "do0")     .side(1) [3]   # якщо X==0 → do0; ніжка HIGH, фронт вгору (+4 такти)
    jmp("bitloop")        .side(1) [11]  # біт «1»: HIGH ще +12 тактів → T1H ≈ 800 нс
    label("do0")
    jmp("bitloop")        .side(0) [7]   # біт «0»: LOW  +8 тактів   → T0H ≈ 400 нс
    wrap()
