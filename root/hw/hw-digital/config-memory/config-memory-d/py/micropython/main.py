from machine import Pin
import time

done = Pin(FPGA_DONE_PIN, Pin.IN)

# Чекаємо, поки FPGA наповнить свою (летку) конфігураційну пам'ять.
# Поки DONE=0 — кристал іще без схеми: комірки заповнюються, виходи невизначені.
def wait_fpga_ready(timeout_ms):
    t = 0
    while not done.value():                  # DONE підніметься, коли всі комірки залито
        if t >= timeout_ms:                  # не дочекалися — конфігурація зірвалася:
            report_error(ERR_CFG_FAILED)     #   порожнє чи побите джерело бітстріму
            return False                     #   (працювати з чипом НЕ можна)
        time.sleep_ms(1)
        t += 1
    return True                              # DONE=1 — пам'ять повна, схема існує, чип готовий
