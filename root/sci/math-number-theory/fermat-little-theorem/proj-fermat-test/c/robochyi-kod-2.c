// портативна заміна mulmod через додавання (вимагає m < 2⁶³)
static uint64_t mulmod(uint64_t a, uint64_t b, uint64_t m) {
    uint64_t r = 0;
    a %= m;
    while (b > 0) {
        if (b & 1) r = (r + a) % m;   // додати поточну сходинку
        a = (a + a) % m;              // подвоїти
        b >>= 1;
    }
    return r;
}
