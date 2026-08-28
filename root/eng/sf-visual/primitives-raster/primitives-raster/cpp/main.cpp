// fb — кадровий буфер W×H, набір пікселів кольору color.
void draw_line(uint16_t *fb, int W, int H,
               int x0, int y0, int x1, int y1, uint16_t color)
{
    int dx =  abs(x1 - x0);
    int dy = -abs(y1 - y0);      // dy від'ємний — спрощує крок похибки
    int sx = x0 < x1 ? 1 : -1;   // напрям по X
    int sy = y0 < y1 ? 1 : -1;   // напрям по Y
    int err = dx + dy;           // ціла похибка, старт = dx + dy

    for (;;) {
        if ((unsigned)x0 < (unsigned)W && (unsigned)y0 < (unsigned)H)
            fb[y0 * W + x0] = color;          // відсікання: лише видимі пікселі
        if (x0 == x1 && y0 == y1) break;      // дійшли кінця
        int e2 = 2 * err;                     // подвоєна похибка — порівнюємо без дробів
        if (e2 >= dy) { err += dy; x0 += sx; } // крок по X
        if (e2 <= dx) { err += dx; y0 += sy; } // крок по Y
    }
}
