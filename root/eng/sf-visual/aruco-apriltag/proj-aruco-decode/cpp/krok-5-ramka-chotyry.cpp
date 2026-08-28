// Порахувати 16-бітний код із матриці внутрішніх 4×4 бітів (рядок за рядком).
static uint16_t bits4x4_to_code(const uint8_t bit[GRID][GRID]) {
    uint16_t code = 0;
    for (int gy = 1; gy <= 4; gy++)                 // внутрішні клітинки 1..4
        for (int gx = 1; gx <= 4; gx++) {
            code <<= 1;
            code |= bit[gy][gx] & 1;
        }
    return code;
}

// Повернути матрицю 4×4 бітів на 90° за годинниковою: dst[x][3-y] = src[y][x].
static void rot90_4x4(const uint8_t src[4][4], uint8_t dst[4][4]) {
    for (int y = 0; y < 4; y++)
        for (int x = 0; x < 4; x++)
            dst[x][3 - y] = src[y][x];
}

static int hamming16(uint16_t a, uint16_t b) {
    uint16_t d = a ^ b; int c = 0;                  // XOR: одиниці там, де біти різні
    while (d) { c += d & 1; d >>= 1; }              // порахувати одиниці (популяція)
    return c;
}

// Словник: коди у ЖОРСТКОМУ порядку рамка-чорна, лише внутрішні 4×4.
// (реальний ArUco зберігає всі 4 оберти заздалегідь; ми обертаємо матрицю на льоту)
typedef struct { const uint16_t *code; int count; int max_correct; } Dict;

// Звірити прочитані біти зі словником по 4 обертах. Повертає id (індекс) або -1.
// *rot — на скільки *90° мітка повернута (0..3), щоб викликач упорядкував кути.
static int identify(const uint8_t bit[GRID][GRID], const Dict *dict, int *rot) {
    // витягти внутрішні 4×4 в окрему матрицю
    uint8_t m[4][4], r[4][4];
    for (int y = 0; y < 4; y++)
        for (int x = 0; x < 4; x++) m[y][x] = bit[y + 1][x + 1];

    int best_id = -1, best_dist = 0x7fffffff, best_rot = 0;
    for (int k = 0; k < 4; k++) {                   // чотири оберти
        // зібрати код поточного оберту
        uint16_t code = 0;
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++) { code <<= 1; code |= m[y][x] & 1; }
        // мінімальний Гемінг до всіх слів словника
        for (int i = 0; i < dict->count; i++) {
            int d = hamming16(code, dict->code[i]);
            if (d < best_dist) { best_dist = d; best_id = i; best_rot = k; }
        }
        rot90_4x4(m, r);                            // повернути на наступні 90°
        memcpy(m, r, sizeof m);
    }
    if (best_dist <= dict->max_correct) {           // у межах виправлення → впізнано
        *rot = best_rot;
        return best_id;
    }
    return -1;                                       // задалеко від усіх → чуже
}
