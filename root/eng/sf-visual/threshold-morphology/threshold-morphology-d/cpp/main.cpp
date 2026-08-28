// B₁: центр білий.  B₂: усі 8 сусідів чорні.
// Ізольована точка = центр 255 І весь окіл 3×3, крім центру, = 0.
uint8_t hitmiss_isolated(const uint8_t m[H][W], int y, int x) {
    if (m[y][x] != 255) return 0;                 // центр мусить бути білим (B₁)
    for (int dy = -1; dy <= 1; dy++)
        for (int dx = -1; dx <= 1; dx++) {
            if (dx == 0 && dy == 0) continue;     // центр пропускаємо
            if (at_clamp(m, y+dy, x+dx) != 0)     // будь-який сусід білий → не ізольована
                return 0;
        }
    return 255;                                    // збігся повний шаблон (B₁ і B₂)
}
