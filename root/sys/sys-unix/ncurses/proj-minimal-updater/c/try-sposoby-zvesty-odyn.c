/* 1. Повне перемальовування: нічого не порівнюємо. */
static size_t redraw_full(Wire *w, const Screen *ns)
{
        for (int y = 0; y < ROWS; y++) {
                cup(w, y, 0);
                for (int x = 0; x < COLS; x++)
                        emit_cell(w, ns->c[y][x]);
        }
        return w->bytes;
}

/* 2. Різниця по комірках: перед кожною групою — своє позиціювання. */
static size_t redraw_diff(Wire *w, const Screen *cur, const Screen *ns)
{
        for (int y = 0; y < ROWS; y++)
                for (int x = 0; x < COLS; x++) {
                        if (cell_eq(cur->c[y][x], ns->c[y][x]))
                                continue;
                        if (w->cy != y || w->cx != x)
                                cup(w, y, x);
                        emit_cell(w, ns->c[y][x]);
                }
        return w->bytes;
}

/* Скільки коштує передрукувати незмінний проміжок [a, b) у рядку y:
   самі знаки плюс перемикання ознак, якщо всередині вони міняються. */
static int gap_cost(const Screen *ns, int y, int a, int b, int attr)
{
        int n = 0;

        for (int x = a; x < b; x++) {
                if (ns->c[y][x].attr != attr) {
                        attr = ns->c[y][x].attr;
                        n += sgr_len(attr);
                }
                n++;
        }
        return n;
}

/* 3. Те саме, але з пам'яттю про те, де вже стоїть курсор. */
static size_t redraw_near(Wire *w, const Screen *cur, const Screen *ns)
{
        for (int y = 0; y < ROWS; y++) {
                int x = 0;

                while (x < COLS) {
                        while (x < COLS && cell_eq(cur->c[y][x], ns->c[y][x]))
                                x++;
                        if (x == COLS)
                                break;
                        if (w->cy != y || w->cx != x)
                                cup(w, y, x);
                        for (;;) {
                                int g;

                                emit_cell(w, ns->c[y][x]);
                                x++;
                                for (g = x; g < COLS && cell_eq(cur->c[y][g], ns->c[y][g]); g++)
                                        ;
                                if (g == COLS)
                                        break;               /* далі в рядку змін немає */
                                if (gap_cost(ns, y, x, g, w->attr) > cup_len(y, g))
                                        break;               /* стрибнути дешевше */
                                while (x < g)                /* пройти розрив наскрізь */
                                        emit_cell(w, ns->c[y][x++]);
                        }
                }
        }
        return w->bytes;
}
