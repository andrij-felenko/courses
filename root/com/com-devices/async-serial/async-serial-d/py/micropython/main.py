from machine import Pin
import time

BIT_US = 1000000 // 9600            # 104 мкс на біт при 9600 бод
tx = Pin(TX_PIN, Pin.OUT)

def uart_tx_byte(b):
    tx.value(0)                     # старт-біт: лінія йде в «0»
    time.sleep_us(BIT_US)
    for _ in range(8):              # 8 біт даних, молодший уперед
        tx.value(b & 1)
        time.sleep_us(BIT_US)
        b >>= 1
    tx.value(1)                     # стоп-біт: лінія назад у спокій «1»
    time.sleep_us(BIT_US)
