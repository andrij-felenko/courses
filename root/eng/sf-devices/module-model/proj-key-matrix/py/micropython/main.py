from machine import Pin
import time

ROWS = 4
COLS = 4
row_gpio = (12, 13, 14, 27)
col_gpio = (16, 17, 18, 19)

# стовпці — входи з підтяжкою (спокій = HIGH)
cols = [Pin(g, Pin.IN, Pin.PULL_UP) for g in col_gpio]
# рядки поки «відпущені» — просто входи
rows = [Pin(g, Pin.IN) for g in row_gpio]

def matrix_scan():
    # повертає 16 бітів: біт (r*COLS + c) = 1, якщо клавішу натиснуто
    keys = 0
    for r in range(ROWS):
        rows[r].init(Pin.OUT)          # активуємо рядок
        rows[r].value(0)               # притягуємо до нуля
        time.sleep_us(5)               # дати лінії осісти

        for c in range(COLS):
            if cols[c].value() == 0:   # стовпець упав → натиск
                keys |= 1 << (r * COLS + c)

        rows[r].init(Pin.IN)           # «відпускаємо» рядок
    return keys
