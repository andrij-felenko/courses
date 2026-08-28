/* Допоміжна функція знаходження степеня многочлена (індекс найстаршого біта) */
static int poly_degree(uint16_t p) {
    int deg = -1;
    while (p > 0) {
        deg++;
        p >>= 1;
    }
    return deg;
}

/* Знаходження мультиплікативно оберненого елемента у GF(2^8) через розширений алгоритм Евкліда */
uint8_t gf_inverse_eea(uint8_t a) {
    if (a == 0) return 0; /* Оберненого для нуля не існує */

    uint32_t r0 = AES_POLY; /* 0x11B (степінь 8) */
    uint32_t r1 = a;        /* степінь < 8 */
    uint32_t v0 = 0;
    uint32_t v1 = 1;

    while (r1 > 1) {
        int deg0 = poly_degree((uint16_t)r0);
        int deg1 = poly_degree((uint16_t)r1);
        int shift = deg0 - deg1;

        if (shift < 0) {
            /* Обмін місцями r0 та r1 */
            uint32_t tmp_r = r0; r0 = r1; r1 = tmp_r;
            uint32_t tmp_v = v0; v0 = v1; v1 = tmp_v;
            shift = -shift;
        }

        r0 ^= (r1 << shift);
        v0 ^= (v1 << shift);
    }

    return (uint8_t)v1;
}
