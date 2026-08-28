// ескіз ковзного SAD уздовж рядка для ОДНОГО фіксованого диспаритету d.
// col_sad[x] тримає вертикальну суму |L−R| по стовпцю x (висотою у вікно).
// тоді SAD вікна = сума col_sad по 2·HALF+1 сусідніх стовпцях, і при зсуві
// вікна вправо ми лише додаємо новий стовпець і віднімаємо той, що вийшов.
static uint16_t col_sad[W];

static void slide_row_for_d(int y, int d)
{
    // 1) порахувати вертикальні суми стовпців один раз на рядок
    for (int x = d; x < W; ++x) {
        uint16_t s = 0;
        for (int j = -HALF; j <= HALF; ++j)
            s += (uint16_t)abs((int)L[y + j][x] - (int)R[y + j][x - d]);
        col_sad[x] = s;
    }
    // 2) перша віконна сума зліва
    uint32_t win = 0;
    for (int x = d; x < d + 2 * HALF + 1; ++x) win += col_sad[x];
    // 3) ковзаємо вікном: +новий стовпець, −старий (О(1) на піксель)
    for (int xc = d + HALF + 1; xc < W - HALF; ++xc) {
        // тут win — це SAD вікна з центром (xc-1) при цьому d;
        // порівнюємо з найкращим для цього пікселя й оновлюємо best/second...
        win += col_sad[xc + HALF];
        win -= col_sad[xc - HALF - 1];
    }
}
