from machine import Pin

data  = Pin(2, Pin.OUT)   # DATA  — послідовні дані
clk   = Pin(3, Pin.OUT)   # CLK   — такт зсуву
latch = Pin(4, Pin.OUT)   # LATCH — такт защіпки

# Засунути один байт у зсувний регістр (старший біт першим)
def shift_out_byte(value):
    for i in range(7, -1, -1):        # від біта 7 (старший) до 0
        data.value((value >> i) & 1)  # 1) виставили дані
        clk.value(1)                  # 2) фронт такту: біт «затік»,
        clk.value(0)                  #    решта зсунулась на щабель

# Показати байт на виходах: засунути 8 бітів, тоді клацнути латчем
def show_byte(value):
    shift_out_byte(value)
    latch.value(1)                    # один імпульс RCLK копіює
    latch.value(0)                    #    рядок у вихідний латч
