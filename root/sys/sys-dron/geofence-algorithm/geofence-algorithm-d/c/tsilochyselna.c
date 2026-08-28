// Оптимізована функція перевірки належності точки полігону на цілих числах.
// Повертає true, якщо точка (px, py) всередині полігона.
// Координати задані у форматі int32_t (градуси * 1e7).

bool point_in_polygon_fixed(int32_t px, int32_t py,
                            const int32_t vx[], const int32_t vy[],
                            uint8_t n) {
    bool inside = false;
    uint8_t j = n - 1;

    for (uint8_t i = 0; i < n; i++) {
        // Перевірка напіввідкритого вертикального інтервалу
        if ((vy[i] <= py && py < vy[j]) || (vy[j] <= py && py < vy[i])) {
            // Векторний добуток без ділення
            int64_t cross = (int64_t)(px - vx[i]) * (int64_t)(vy[j] - vy[i]) -
                            (int64_t)(py - vy[i]) * (int64_t)(vx[j] - vx[i]);

            if (vy[i] < vy[j]) {
                // Ребро спрямоване вгору: перетин праворуч, якщо cross < 0
                if (cross < 0) inside = !inside;
            } else {
                // Ребро спрямоване вниз: перетин праворуч, якщо cross > 0
                if (cross > 0) inside = !inside;
            }
        }
        j = i;
    }
    return inside;
}
