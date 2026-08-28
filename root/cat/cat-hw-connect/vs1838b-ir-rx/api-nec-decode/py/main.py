# --- Ручний декодер NEC на MicroPython (ESP32 / Pico) ---
# OUT приймача → GPIO 4 (будь-який вивід з підтримкою переривань)
from machine import Pin
import time

PIN_IR = 4
gaps = []                       # проста черга інтервалів між спадами
last_fall = time.ticks_us()

def on_fall(pin):               # ISR: коротко! зняти час, покласти інтервал, вийти
    global last_fall
    now = time.ticks_us()
    gaps.append(time.ticks_diff(now, last_fall))   # ticks_diff коректно рахує навіть на переповненні лічильника
    last_fall = now

ir = Pin(PIN_IR, Pin.IN)
ir.irq(trigger=Pin.IRQ_FALLING, handler=on_fall)

state = "IDLE"
bits = 0
nbits = 0
last_value = 0

def within(v, target):          # допуск ±30% під тремтіння дешевих пультів
    return target * 0.7 < v < target * 1.3

def handle_gap(gap):
    global state, bits, nbits, last_value
    if within(gap, 13500):                  # преамбула повного кадру
        state, bits, nbits = "DATA", 0, 0
        return
    if within(gap, 11250):                  # код-повтор: кнопку тримають
        addr = last_value & 0xFF
        cmd  = (last_value >> 16) & 0xFF
        print("ПОВТОР (тримають): addr=0x%02X cmd=0x%02X" % (addr, cmd))
        state = "IDLE"
        return
    if state == "DATA":
        bit = 1 if gap > 1200 else 0        # поріг між ~1.1 і ~2.2 мс
        bits |= (bit << nbits)              # молодший біт уперед
        nbits += 1
        if nbits == 32:
            decode_frame(bits)
            state = "IDLE"

def decode_frame(raw):
    global last_value
    addr  =  raw        & 0xFF
    addr_n = (raw >> 8)  & 0xFF
    cmd   = (raw >> 16) & 0xFF
    cmd_n  = (raw >> 24) & 0xFF
    ok = ((addr ^ addr_n) == 0xFF) and ((cmd ^ cmd_n) == 0xFF)
    last_value = raw
    tag = "[XOR ok]" if ok else "[XOR BAD або extended-NEC]"
    print("addr=0x%02X cmd=0x%02X  %s" % (addr, cmd, tag))

while True:                                 # головний цикл: забрати з черги все накопичене
    while gaps:
        handle_gap(gaps.pop(0))
