# fb — кадровий буфер W×H (плаский список), набір пікселів кольору color.
def draw_line(fb, W, H, x0, y0, x1, y1, color):
    dx =  abs(x1 - x0)
    dy = -abs(y1 - y0)           # dy від'ємний — спрощує крок похибки
    sx = 1 if x0 < x1 else -1    # напрям по X
    sy = 1 if y0 < y1 else -1    # напрям по Y
    err = dx + dy                # ціла похибка, старт = dx + dy

    while True:
        if 0 <= x0 < W and 0 <= y0 < H:
            fb[y0 * W + x0] = color        # відсікання: лише видимі пікселі
        if x0 == x1 and y0 == y1:
            break                          # дійшли кінця
        e2 = 2 * err                       # подвоєна похибка — порівнюємо без дробів
        if e2 >= dy:                       # крок по X
            err += dy
            x0 += sx
        if e2 <= dx:                       # крок по Y
            err += dx
            y0 += sy
