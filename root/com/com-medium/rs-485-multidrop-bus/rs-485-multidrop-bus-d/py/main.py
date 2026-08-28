# MicroPython: DE і RE зведені в один пін (DE=1 → передаємо, DE=0 → слухаємо)
from machine import Pin, UART

de = Pin(4, Pin.OUT)
uart = UART(1, baudrate=9600, bits=8, parity=None, stop=1)

def rs485_send(buf):
    de.value(1)          # беремо лінію: вузол говорить
    uart.write(buf)      # штовхаємо байти в апаратний UART
    uart.flush()         # ЧЕКАЄМО, поки піде ОСТАННІЙ стоп-біт
    de.value(0)          # відпускаємо лінію: знову слухаємо
