// Оцінка коефіцієнтів методом «сірий світ».
// Пише в gR,gG,gB коефіцієнти у форматі Q8.8 (256 == 1.0). Опорний канал — G.
void estimate_gray_world(const RGB *img, int n,
                         uint16_t *gR, uint16_t *gG, uint16_t *gB) {
    uint64_t sumR = 0, sumG = 0, sumB = 0;   // 64 біти: сума мільйонів байтів переповнить 32
    for (int i = 0; i < n; i++) {
        sumR += img[i].r;
        sumG += img[i].g;
        sumB += img[i].b;
    }
    if (sumR == 0) sumR = 1;                  // захист від ділення на нуль (чорний канал)
    if (sumB == 0) sumB = 1;
    if (sumG == 0) sumG = 1;

    *gG = ONE;                                // зелений — опорний, коефіцієнт 1.0
    *gR = (uint16_t)((sumG << Q) / sumR);     // <<Q ПЕРЕД діленням → результат уже в Q8.8
    *gB = (uint16_t)((sumG << Q) / sumB);
}
