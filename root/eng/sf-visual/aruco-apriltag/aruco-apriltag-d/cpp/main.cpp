// warped — розпрямлене зображення мітки, W×W пікселів, 8 біт/піксель, рядок = W байтів.
// GRID=6 (з рамкою); внутрішні 4×4 несуть дані. Повертаємо 16-бітний сирий код.
#define GRID 6
#define CELL (W / GRID)          // скільки пікселів припадає на одну клітинку

// Середня яскравість клітинки (gx,gy) — беремо серединку клітинки, без країв.
static int cell_mean(const uint8_t *warped, int W, int gx, int gy) {
    int x0 = gx * CELL + CELL / 4;      // відступ від краю клітинки, щоб не чіпати
    int y0 = gy * CELL + CELL / 4;      // сусідню (краї «пливуть» після розпрямлення)
    int x1 = gx * CELL + 3 * CELL / 4;
    int y1 = gy * CELL + 3 * CELL / 4;
    long sum = 0; int n = 0;
    for (int y = y0; y < y1; y++)
        for (int x = x0; x < x1; x++) { sum += warped[y * W + x]; n++; }
    return (int)(sum / n);              // 0..255
}

// Перевірити рамку й прочитати внутрішні 4×4 у 16-бітний код (чорне=0, біле=1).
static int read_marker(const uint8_t *warped, int W, uint16_t *code_out) {
    const int THR = 128;               // поріг чорне/біле (спрощено; краще адаптивний)
    // 1) Рамка: усе зовнішнє кільце має бути ЧОРНЕ, інакше це не мітка.
    for (int g = 0; g < GRID; g++)
        if (cell_mean(warped, W, g, 0)        > THR ||   // верхній край
            cell_mean(warped, W, g, GRID - 1) > THR ||   // нижній край
            cell_mean(warped, W, 0, g)        > THR ||   // лівий край
            cell_mean(warped, W, GRID - 1, g) > THR)     // правий край
            return 0;                  // рамка пробита — відкинути кандидата
    // 2) Внутрішні 4×4 → біти коду.
    uint16_t code = 0;
    for (int gy = 1; gy <= 4; gy++)
        for (int gx = 1; gx <= 4; gx++) {
            code <<= 1;
            if (cell_mean(warped, W, gx, gy) > THR) code |= 1;   // біла = 1
        }
    *code_out = code;
    return 1;                          // код прочитано; далі — звірка зі словником
}
