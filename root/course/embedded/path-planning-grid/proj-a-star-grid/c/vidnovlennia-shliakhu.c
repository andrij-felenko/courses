// Відновити шлях у out[] (у клітинних індексах), від старту до цілі.
// Повертає кількість точок, або 0, якщо не влізло в out_cap.
static int astar_reconstruct(int gx, int gy, int32_t *out, int out_cap) {
    // 1) Пройти came_from від цілі назад, складаючи в out задом наперед.
    int n = 0;
    int32_t node = idx_of(gx, gy);
    while (node != -1) {
        if (n >= out_cap) return 0;   // шлях довший за буфер — чесно програємо
        out[n++] = node;
        node = came_from[node];       // ще крок до старту
    }
    // 2) Розвернути: тепер out[0] стане стартом, out[n-1] — ціллю.
    for (int i = 0, j = n - 1; i < j; i++, j--) {
        int32_t t = out[i]; out[i] = out[j]; out[j] = t;
    }
    return n;
}
