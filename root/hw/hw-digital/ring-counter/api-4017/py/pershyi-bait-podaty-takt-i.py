import time
import gpiod  # керування GPIO на одноплатнику (Linux)

# Ніжки контролера, з'єднані з лічильником:
PIN_CLK = 6    # → CLK (крок по фронту 0→1)
PIN_MR  = 7    # → MR  (скид у Q0; 1 = скинути)

chip = gpiod.Chip("gpiochip0")
clk = chip.get_line(PIN_CLK); clk.request("chaser", gpiod.LINE_REQ_DIR_OUT)
mr  = chip.get_line(PIN_MR);  mr.request("chaser", gpiod.LINE_REQ_DIR_OUT)

def chaser_init():
    # Скид на старті: коротким MR=1 гарантовано ставимо лічильник у Q0.
    # Це прибирає ризик стартувати з невизначеного стану (див. «граблі»).
    mr.set_value(1)
    mr.set_value(0)       # відпустили скид — тепер рахуємо від Q0
    clk.set_value(0)      # такт у низькому, чекає на фронт

def chaser_step():
    # Один крок вогника: даємо рівно один фронт 0→1 на CLK.
    clk.set_value(1)      # фронт наростання — лічильник крокує на наступний вихід
    clk.set_value(0)      # повертаємо CLK у низький, готуючи наступний фронт

chaser_init()
while True:
    chaser_step()         # активний вихід перескочив на сусідній Qn
    time.sleep(0.1)       # темп вогника: 10 кроків/с → повне коло за ~1 с
