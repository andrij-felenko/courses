rows = []
cols = []

def keypad_begin():
    # Рядки — входи з ВНУТРІШНЬОЮ підтяжкою: спокій = HIGH, натиск потягне в LOW.
    for p in ROW_PIN:
        rows.append(Pin(p, Pin.IN, Pin.PULL_UP))

    # Стовпці — виходи, і в СПОКОЇ тримаємо їх HIGH (неактивні).
    # Активним стовпець стане лише на мить свого скану (виставимо LOW).
    for p in COL_PIN:
        col = Pin(p, Pin.OUT)
        col.value(1)          # неактивний стовпець = HIGH
        cols.append(col)
