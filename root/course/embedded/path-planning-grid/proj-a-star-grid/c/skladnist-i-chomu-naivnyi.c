// Роздути перешкоди на radius клітин: кожну стіну «розмазати» на сусідів.
// Пишемо в окрему мапу, щоб не роздувати вже роздуте (інакше стіни «поповзуть»).
static void inflate_obstacles(const uint8_t *src, uint8_t *dst, int radius) {
    for (int y = 0; y < GRID_H; y++)
        for (int x = 0; x < GRID_W; x++) {
            uint8_t occupied = 0;
            // Клітина зайнята, якщо в радіусі є хоч одна стіна вихідної мапи.
            for (int oy = -radius; oy <= radius && !occupied; oy++)
                for (int ox = -radius; ox <= radius; ox++) {
                    int sx = x + ox, sy = y + oy;
                    if (sx < 0 || sx >= GRID_W || sy < 0 || sy >= GRID_H) continue;
                    if (src[idx_of(sx, sy)]) { occupied = 1; break; }
                }
            dst[idx_of(x, y)] = occupied;
        }
}
