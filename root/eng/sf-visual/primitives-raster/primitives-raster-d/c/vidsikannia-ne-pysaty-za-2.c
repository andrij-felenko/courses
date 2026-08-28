// Cohen–Sutherland: обрізати лінію до вікна [xmin..xmax]×[ymin..ymax].
// Повертає 1, якщо лишився видимий відрізок (кінці оновлено), інакше 0.
int clip_line(int *x0, int *y0, int *x1, int *y1,
              int xmin, int ymin, int xmax, int ymax)
{
    int c0 = outcode(*x0, *y0, xmin, ymin, xmax, ymax);
    int c1 = outcode(*x1, *y1, xmin, ymin, xmax, ymax);
    for (;;) {
        if ((c0 | c1) == 0) return 1;           // обидва у вікні — приймаємо
        if ((c0 & c1) != 0) return 0;           // обидва за межею — відкидаємо
        int c = c0 ? c0 : c1;                    // кінець, що зовні
        int x = 0, y = 0;
        if (c & OUT_TOP) {                       // перетин з верхньою межею
            x = *x0 + (*x1 - *x0) * (ymax - *y0) / (*y1 - *y0); y = ymax;
        } else if (c & OUT_BOTTOM) {
            x = *x0 + (*x1 - *x0) * (ymin - *y0) / (*y1 - *y0); y = ymin;
        } else if (c & OUT_RIGHT) {
            y = *y0 + (*y1 - *y0) * (xmax - *x0) / (*x1 - *x0); x = xmax;
        } else { /* OUT_LEFT */
            y = *y0 + (*y1 - *y0) * (xmin - *x0) / (*x1 - *x0); x = xmin;
        }
        if (c == c0) { *x0 = x; *y0 = y; c0 = outcode(x, y, xmin, ymin, xmax, ymax); }
        else         { *x1 = x; *y1 = y; c1 = outcode(x, y, xmin, ymin, xmax, ymax); }
    }
}
