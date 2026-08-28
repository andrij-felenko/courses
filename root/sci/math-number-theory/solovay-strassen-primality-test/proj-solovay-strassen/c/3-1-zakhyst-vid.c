/* Альтернативне модульне множення для систем без 128-бітних типів */
static uint64_t mul_mod_safe(uint64_t a, uint64_t b, uint64_t mod) {
    uint64_t res = 0;
    a %= mod;
    while (b > 0) {
        if (b & 1) {
            res = (res >= mod - a) ? (res - (mod - a)) : (res + a);
        }
        a = (a >= mod - a) ? (a - (mod - a)) : (a + a);
        b >>= 1;
    }
    return res;
}
