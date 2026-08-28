// Поріг 99-го перцентиля одного каналу через гістограму 256 комірок.
// hist[v] — скільки пікселів мали значення v. Повертає найменше t, вище за яке
// лежить не більше ~1% пікселів (тобто «майже-максимум», стійкий до викидів).
static uint8_t percentile_top(const uint32_t hist[256], int total) {
    uint32_t cut = (uint32_t)total / 100;   // 1% пікселів дозволяємо відкинути як викиди
    uint32_t acc = 0;
    for (int v = 255; v >= 0; v--) {
        acc += hist[v];
        if (acc >= cut)
            return (uint8_t)v;               // на цьому біні набрався верхній 1%
    }
    return 0;                                // канал порожній — не станеться при total>0
}

// Оцінка коефіцієнтів методом «біла пляма» на перцентилі (Q8.8, опорний G).
void estimate_white_patch(const RGB *img, int n,
                          uint16_t *gR, uint16_t *gG, uint16_t *gB) {
    uint32_t hR[256] = {0}, hG[256] = {0}, hB[256] = {0};
    for (int i = 0; i < n; i++) {            // один прохід — три гістограми
        hR[img[i].r]++;
        hG[img[i].g]++;
        hB[img[i].b]++;
    }
    uint8_t pR = percentile_top(hR, n);      // «майже-пік» кожного каналу
    uint8_t pG = percentile_top(hG, n);
    uint8_t pB = percentile_top(hB, n);
    if (pR == 0) pR = 1;                      // захист від ділення на нуль
    if (pG == 0) pG = 1;
    if (pB == 0) pB = 1;

    // Рівняємо «майже-пік» кожного каналу до опорного pG (а не всі до 255):
    // так канали лишаються між собою збалансовані, а не роздуті поодинці.
    *gG = ONE;
    *gR = (uint16_t)(((uint32_t)pG << Q) / pR);
    *gB = (uint16_t)(((uint32_t)pG << Q) / pB);
}
