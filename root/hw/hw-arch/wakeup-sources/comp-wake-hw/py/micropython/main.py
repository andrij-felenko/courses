from machine import Pin

# ПЕРШИМ — утримати живлення, поки кнопку ще тримають
hold = Pin(4, Pin.OUT, value=1)          # latch on: одразу HIGH
key  = Pin(5, Pin.IN, Pin.PULL_UP)       # читає стан кнопки

# ... решта ініціалізації ...

def power_off():
    # Самовимкнення: знімаємо утримання — живлення рветься
    hold.value(0)
    # Цей рядок вже не виконається — МК мертвий
