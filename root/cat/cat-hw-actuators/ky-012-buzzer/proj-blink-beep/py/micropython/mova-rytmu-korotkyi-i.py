from machine import Pin
import time

buzzer = Pin(8, Pin.OUT)
buzzer.value(0)

def beep(ms):
    buzzer.value(1)
    time.sleep_ms(ms)
    buzzer.value(0)

# N однакових біпів по on мс з паузою gap мс між ними.
def beep_n(n, on, gap):
    for i in range(n):
        beep(on)
        if i < n - 1:
            time.sleep_ms(gap)      # паузу — МІЖ біпами, не після останнього

# Іменовані сигнали — зручні назви для конкретних ритмів.
def signal_ready():     beep(120)              # готово: один короткий
def signal_error():     beep_n(3, 60, 80)      # помилка: три швидкі
def signal_attention(): beep(600)              # увага: один довгий
def alarm(times):       beep_n(times, 400, 200)  # тривога: довгі з паузами

while True:
    signal_ready()
    time.sleep_ms(1500)
    signal_error()
    time.sleep_ms(1500)
    alarm(3)
    time.sleep_ms(3000)
