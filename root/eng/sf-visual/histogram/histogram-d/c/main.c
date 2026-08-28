void build_lut(const uint32_t hist[256], uint32_t n, uint8_t lut[256])
{
    if (n == 0) {                              // порожній кадр — ділити нема на що
        for (int v = 0; v < 256; ++v) lut[v] = (uint8_t)v;   // тотожна таблиця
        return;
    }
    uint32_t acc = 0;                          // накопичена сума = CDF·n
    for (int v = 0; v < 256; ++v) {
        acc += hist[v];                        // acc = h(0)+…+h(v)
        // round( (acc/n)·255 ) = (acc·255 + n/2) / n   — цілочисельно
        uint32_t mapped = (acc * 255u + n / 2u) / n;
        lut[v] = (uint8_t)mapped;              // 0…255 гарантовано (acc ≤ n)
    }
}
