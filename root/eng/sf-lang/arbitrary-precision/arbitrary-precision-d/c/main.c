// r[0..n-1] += a[0..n-1] * b, повертає перенос назовні
static uint64_t mul_add_limb(uint64_t *r, const uint64_t *a, size_t n, uint64_t b) {
    uint64_t carry = 0;
    for (size_t i = 0; i < n; i++) {
        unsigned __int128 t = (unsigned __int128)a[i] * b + r[i] + carry;
        r[i]  = (uint64_t)t;          // молодше слово лишається на місці
        carry = (uint64_t)(t >> 64);  // старше стає переносом далі
    }
    return carry;
}
