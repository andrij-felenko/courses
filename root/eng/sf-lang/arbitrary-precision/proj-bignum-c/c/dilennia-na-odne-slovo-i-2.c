#if LIMB_BITS == 64
  #define DEC_CHUNK    UINT64_C(10000000000000000000)  // 10¹⁹ < 2⁶⁴
  #define DEC_DIGITS   19
  #define DEC_PER_LIMB 20        // 2⁶⁴−1 має рівно 20 цифр
#else
  #define DEC_CHUNK    UINT32_C(1000000000)            // 10⁹ < 2³²
  #define DEC_DIGITS   9
  #define DEC_PER_LIMB 10
#endif

// десятковий запис; звільняє буфер той, хто викликав
char *big_to_dec(const big *x) {
    size_t cap = x->n * DEC_PER_LIMB + 2;     // цифри + знак + '\0'
    if (cap < 3) cap = 3;
    char *s = malloc(cap);
    if (!s) abort();
    size_t pos = cap;
    s[--pos] = '\0';
    if (x->n == 0) { s[--pos] = '0'; memmove(s, s + pos, cap - pos); return s; }

    big t = {0};                              // ділення руйнівне — працюємо з копією
    big_reserve(&t, x->n);
    memcpy(t.d, x->d, x->n * sizeof *t.d);
    t.n = x->n;

    while (t.n > 0) {                         // пишемо з кінця буфера
        limb rem = div_limb(&t, DEC_CHUNK);
        for (int k = 0; k < DEC_DIGITS; k++) {
            s[--pos] = (char)('0' + rem % 10);
            rem /= 10;
            if (t.n == 0 && rem == 0) break;  // старша група — без ведучих нулів
        }
    }
    if (x->neg) s[--pos] = '-';
    free(t.d);
    memmove(s, s + pos, cap - pos);
    return s;
}
