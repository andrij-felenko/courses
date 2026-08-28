uint32_t adler32_simd(const uint8_t *d, size_t n) {
    uint32_t a = 1, b = 0;

    while (n) {
        size_t k = n < NMAX ? n : NMAX;   /* межа та сама: вона про кількість байтів,
                                             а не про спосіб їх лічити */
        n -= k;
        size_t j = 0;
        for (; j + 16 <= k; j += 16)
            adler_block16(d + j, &a, &b);
        for (; j < k; j++) { a += d[j]; b += a; }   /* хвіст — скалярно */
        d += k;
        a %= BASE;
        b %= BASE;
    }
    return (b << 16) | a;
}
