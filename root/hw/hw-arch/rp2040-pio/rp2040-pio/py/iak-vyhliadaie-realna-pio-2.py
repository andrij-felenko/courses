import rp2
from machine import Pin

WS2812_PIN = 16
# autopull 24 біти (GRB) і напрям зсуву задано в декораторі @rp2.asm_pio(ws2812) вище

sm = rp2.StateMachine(0, ws2812,                                # залити програму
                      freq=800_000 * 25,                        # автомат на 20 МГц
                      sideset_base=Pin(WS2812_PIN))             # ніжка DATA
sm.active(1)                                                    # пуск

def ws2812_send(pixels):
    for px in pixels:
        sm.put(px << 8)                                        # ядро лише годує FIFO
