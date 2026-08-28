import rp2
from machine import Pin

WS2812_PIN = 16
# autopull 24 біти (GRB) і напрям зсуву задано в декораторі @rp2.asm_pio(ws2812)

# 1. залити програму + 2. ніжка DATA + 3. 20 МГц автомата (800 кГц × 25 тактів)
sm = rp2.StateMachine(0, ws2812,
                      freq=800_000 * 25,
                      sideset_base=Pin(WS2812_PIN))
sm.active(1)                                                    # 6. пуск

def ws2812_send_grb(pixels):
    # Ядро лише висипає пікселі у FIFO — далі автомат жене протокол сам
    for px in pixels:
        sm.put(px << 8)
