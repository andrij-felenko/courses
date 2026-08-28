OVERSAMPLE = 16

# Прийняти один кадр 8N1 на голій ніжці. Читання — по центру кожного біта.
# tick() блокує рівно на 1/(16·baud); pin() віддає поточний рівень лінії.
def soft_uart_rx():
    while pin() == 1:                       # чекаємо перепад спокій→старт
        pass

    # переміститися в СЕРЕДИНУ старт-біта й перевірити, що це не голка шуму
    for _ in range(OVERSAMPLE // 2):
        tick()
    if pin() != 0:
        return None                         # фальшивий старт — відкинути

    data = 0
    for i in range(8):
        for _ in range(OVERSAMPLE):
            tick()                          # крок на цілий біт
        data |= (pin() & 1) << i            # зчитуємо по центру, D0 першим

    for _ in range(OVERSAMPLE):
        tick()
    if pin() != 1:
        return None                         # стоп не «1» → помилка кадру

    return data
