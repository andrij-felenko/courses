import rp2
from machine import Pin

WS2812_PIN = 16
# зсув ліворуч, autopull і поріг 24 задано в декораторі @rp2.asm_pio(ws2812) вище

# freq = 800 кГц × 25 тактів = 20 МГц (дільник 6.25 рахує рушій MicroPython)
sm = rp2.StateMachine(0, ws2812,
                      freq=800_000 * 25,
                      sideset_base=Pin(WS2812_PIN))            # ніжка під side-set
sm.active(1)

def ws2812_send(pixels):
    for px in pixels:
        sm.put(px << 8)                                       # вирівняти GRB у старші 24 біти
