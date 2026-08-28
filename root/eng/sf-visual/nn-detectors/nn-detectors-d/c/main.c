#define S 13
#define B 3
#define C 20
#define STRIDE 32                  // 416 / 13
#define K (B*5 + C)                // глибина на клітинку = 35

static float sigmoidf(float x) { return 1.0f / (1.0f + expf(-x)); }

// out — масив [S*S*K], розкладка «по клітинках»: спершу всі K чисел клітинки (0,0),
// потім клітинки (0,1) і т.д. cell_x, cell_y — індекси клітинки; a — номер якоря.
box_t decode_box(const float *out, int cell_x, int cell_y, int a,
                 const float anchor_w[B], const float anchor_h[B]) {
    int cell = (cell_y * S + cell_x) * K;      // початок вектора клітинки
    const float *t = out + cell + a * 5;       // п'ятірка цього якоря

    float bx = (cell_x + sigmoidf(t[0])) * STRIDE;   // центр X у пікселях
    float by = (cell_y + sigmoidf(t[1])) * STRIDE;   // центр Y у пікселях
    float bw = anchor_w[a] * expf(t[2]);             // ширина у пікселях
    float bh = anchor_h[a] * expf(t[3]);             // висота у пікселях

    box_t b;
    b.x1 = bx - bw * 0.5f;     // з центру+розміру → кути
    b.y1 = by - bh * 0.5f;
    b.x2 = bx + bw * 0.5f;
    b.y2 = by + bh * 0.5f;
    return b;
}
