from machine import Pin
import time

ROWS, COLS = 4, 4
row_gp = (9, 8, 7, 6)   # R1..R4
col_gp = (5, 4, 3, 2)   # C1..C4

# що надруковано на клавіатурі: [рядок][стовпець]
keymap = (
    ('1', '2', '3', 'A'),
    ('4', '5', '6', 'B'),
    ('7', '8', '9', 'C'),
    ('*', '0', '#', 'D'),
)

# рядки: входи з підтяжкою, у спокої «1»
rows = [Pin(gp, Pin.IN, Pin.PULL_UP) for gp in row_gp]
# стовпці поки відпущені у вхід (Z)
cols = [Pin(gp, Pin.IN) for gp in col_gp]

def scan_once():
    for c in range(COLS):
        cols[c].init(Pin.OUT)        # цей стовпець беремо виходом
        cols[c].value(0)             # і жену його в «0»
        for r in range(ROWS):
            if rows[r].value() == 0: # рядок упав → тут клавіша
                cols[c].init(Pin.IN) # повертаємо стовпець у Z
                return keymap[r][c]
        cols[c].init(Pin.IN)         # не знайшли — відпускаємо назад у Z
    return None                      # нічого не натиснуто

prev = None
while True:
    k = scan_once()
    if k and k != prev:              # ловимо МОМЕНТ натискання, не утримання
        print("клавіша:", k)
    prev = k
    time.sleep_ms(20)                # грубий антидеренч + не молотимо марно
