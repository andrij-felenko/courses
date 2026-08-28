/* друк n молодших бітів v старшим уперед — портативно, без %b */
static void pbits(const char *tag, uint16_t v, int n) {
    printf("%s", tag);
    for (int i = n - 1; i >= 0; --i) putchar(((v >> i) & 1) ? '1' : '0');
    putchar('\n');
}

int main(void) {
    uint16_t msg  = 0x0Au;                 /* дані 1010                    */
    uint16_t code = encode(msg);           /* → 1010011                    */
    pbits("дані      m = ", msg,  K);
    pbits("код       c = ", code, N);
    pbits("код(LFSR) c = ", encode_lfsr(msg), N);   /* та сама остача */

    uint16_t recv = code ^ (1u << 4);      /* внесемо одну помилку: розряд x⁴ */
    pbits("прийнято  r = ", recv, N);
    pbits("синдром   s = ", syndrome(recv), R);      /* 110 ≠ 0 */

    int ok;
    uint16_t fixed = decode(recv, &ok);
    pbits("виправл.  c = ", fixed, N);
    pbits("відновл.  m = ", (uint16_t)(fixed >> R), K);
    printf("ok = %d\n", ok);
    return 0;
}
