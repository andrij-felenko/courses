/* s = (s − 2) mod Mp,  вхід s ∈ [0, Mp) */
static void sub2_mod_mp(limb *s, int p, int n) {
    int R = p % 32, above = 0;
    for (int i = 1; i < n; i++) if (s[i]) above = 1;
    if (!(s[0] >= 2 || above)) {               /* s дорівнює 0 або 1: спершу + Mp */
        limb d = 2 - s[0];
        for (int i = 0; i < n; i++) s[i] = 0xFFFFFFFFu;
        s[n - 1] = (1u << R) - 1;               /* s = Mp */
        limb b = d;                             /* далі відняти d ∈ {1,2} */
        for (int i = 0; i < n && b; i++) { limb o = s[i]; s[i] = o - b; b = (o < b); }
        return;
    }
    limb b = 2;                                 /* s ≥ 2: проста позика */
    for (int i = 0; i < n && b; i++) { limb o = s[i]; s[i] = o - b; b = (o < b); }
}

int lucas_lehmer(int p) {                       /* p — непарне просте */
    if (p == 2) return 1;
    int n = (p + 31) / 32;
    limb s[n], prod[2 * n];                      /* демо-буфери на стеку */
    memset(s, 0, n * sizeof(limb));
    s[0] = 4;                                    /* S₀ = 4 */
    for (int k = 0; k < p - 2; k++) {
        square(s, n, prod);                     /* prod = s²          (2n лімбів) */
        reduce_mod_mp(prod, p, s, n);           /* s = prod mod Mp    (n лімбів)  */
        sub2_mod_mp(s, p, n);                   /* s = s − 2                     */
    }
    for (int i = 0; i < n; i++) if (s[i]) return 0;
    return 1;                                    /* Sₚ₋₂ ≡ 0 ⇒ Mp просте */
}
