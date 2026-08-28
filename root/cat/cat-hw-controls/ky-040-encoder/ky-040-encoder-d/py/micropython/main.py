from machine import Pin

PIN_CLK = 2                      # квадратурна доріжка A
PIN_DT  = 3                      # квадратурна доріжка B
PIN_SW  = 4                      # кнопка під валом

clk = Pin(PIN_CLK, Pin.IN)       # на платі вже є підтяжка на CLK
dt  = Pin(PIN_DT,  Pin.IN)       # і на DT
sw  = Pin(PIN_SW,  Pin.IN, Pin.PULL_UP)  # а на кнопці підтяжки НЕМА — вмикаємо внутрішню

counter = 0                      # накопичене значення (змінюється в перериванні)

def on_clk_fall(pin):
    # спрацювало на спадному краї CLK: у цю мить рівень DT каже напрям
    global counter
    if dt.value():               # DT ще «1» → за годинниковою
        counter += 1
    else:                        # DT уже «0» → проти
        counter -= 1

clk.irq(trigger=Pin.IRQ_FALLING, handler=on_clk_fall)

shown = 0
while True:
    if counter != shown:         # друкуємо, лише коли значення змінилось
        shown = counter
        print(shown)
    if sw.value() == 0:          # натиск = скидання (LOW, бо pull-up)
        counter = 0
