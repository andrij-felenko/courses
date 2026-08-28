// Покриття пікселя через суперсемплінг 4×4:
// inside(px,py) — чи лежить підпіксель усередині контуру (scanline-тест).
uint8_t coverage4x4(int cellX, int cellY) {
    int hits = 0;
    for (int sy = 0; sy < 4; sy++)
        for (int sx = 0; sx < 4; sx++)
            if (inside(cellX * 4 + sx, cellY * 4 + sy))
                hits++;                       // 0..16 залитих підпікселів
    return (uint8_t)hits;                     // рівень сірого, 0..16
}
