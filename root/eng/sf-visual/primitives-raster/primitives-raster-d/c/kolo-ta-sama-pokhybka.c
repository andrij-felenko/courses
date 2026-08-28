// Коло радіуса r з центром (cx,cy): один октант + вісім дзеркал, самі int.
void draw_circle(uint16_t *fb, int W, int H,
                 int cx, int cy, int r, uint16_t color)
{
    int x = 0, y = r;
    int d = 1 - r;                 // вирішальна змінна, старт F(1, r-½)≈1-r
    while (x <= y) {
        plot8(fb, W, H, cx, cy, x, y, color);   // вісім симетричних точок
        if (d < 0) {               // середина всередині кола → крок E
            d += 2 * x + 3;
        } else {                   // середина зовні → крок SE
            d += 2 * (x - y) + 5;
            y--;
        }
        x++;
    }
}
