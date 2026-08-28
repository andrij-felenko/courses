from machine import Pin

# --- Опитування: цикл сам перевіряє ---
btn = Pin(BTN, Pin.IN, Pin.PULL_UP)
while True:
    if btn.value() == 0:          # натиснуто
        pass
    # ... інша робота, що затримує перевірку

# --- Переривання: подія сама кличе ---
pressed = False                   # прапорець

def on_press(pin):                # обробник: КОРОТКО
    global pressed
    pressed = True                # лише підняти прапорець

btn = Pin(BTN, Pin.IN, Pin.PULL_UP)                 # увімкнути підтяжку
btn.irq(handler=on_press, trigger=Pin.IRQ_FALLING)  # повісити «дзвоник»

while True:
    if pressed:                   # цикл вільний, реакція вмить
        pressed = False
        pass                      # обробити натиск
