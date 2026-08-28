int main(void) {
    int m = 3, r = 1, n = 1 << m;
    int msg[RM_MAXN] = {0}, code[RM_MAXN], recv[RM_MAXN], out[RM_MAXN];

    /* f = 1 ⊕ x₂ ⊕ x₃.  Маски: 1→x₃, 2→x₂, 4→x₁ */
    msg[0] = 1; msg[2] = 1; msg[1] = 1;

    rm_encode(m, msg, code);
    for (int t = 0; t < n; t++) recv[t] = code[t];
    recv[2] ^= 1;                          /* канал псує точку 010 = індекс 2 */

    rm_decode_reed(m, r, recv, out);
    printf("Рід:    a0=%d  x1=%d  x2=%d  x3=%d\n", out[0], out[4], out[2], out[1]);

    rm_decode_fht(m, recv, out);
    printf("Адамар: a0=%d  x1=%d  x2=%d  x3=%d\n", out[0], out[4], out[2], out[1]);
    return 0;
}
