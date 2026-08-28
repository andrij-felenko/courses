/* Точне цілочисельне округлення до найближчого цілого без float */
static inline int64_t div_round_int64(int64_t num, int64_t den) {
    if (den < 0) {
        num = -num;
        den = -den;
    }
    if (num >= 0) {
        return (num + den / 2) / den;
    } else {
        return (num - den / 2) / den;
    }
}

/* Результат ділення з остачею */
typedef struct {
    gauss_t q;  /* частка */
    gauss_t r;  /* остача */
} gauss_div_t;

/* Ділення з остачею: a = b * q + r, де N(r) <= 0.5 * N(b) */
gauss_div_t gauss_div_rem(gauss_t a, gauss_t b) {
    gauss_div_t res;
    uint64_t den = gauss_norm(b);
    if (den == 0) {
        fprintf(stderr, "Помилка: ділення на нуль у кільці ℤ[i]\n");
        exit(EXIT_FAILURE);
    }

    /* Чисельник комплексного дробу a * conj(b) */
    int64_t num_re = a.re * b.re + a.im * b.im;
    int64_t num_im = a.im * b.re - a.re * b.im;

    /* Округлення дійсної та уявної частин до найближчих цілих */
    res.q.re = div_round_int64(num_re, (int64_t)den);
    res.q.im = div_round_int64(num_im, (int64_t)den);

    /* Остача r = a - q * b */
    gauss_t qb = gauss_mul(res.q, b);
    res.r = gauss_sub(a, qb);
    return res;
}

/* Алгоритм Евкліда для знаходження найбільшого спільного дільника */
gauss_t gauss_gcd(gauss_t a, gauss_t b) {
    while (!gauss_is_zero(b)) {
        gauss_div_t d = gauss_div_rem(a, b);
        a = b;
        b = d.r;
    }
    return a;
}

/* Приведення числа до канонічного вигляду у першому квадранті (re > 0, im >= 0) */
gauss_t gauss_canonical(gauss_t a) {
    if (gauss_is_zero(a)) return a;
    gauss_t units[4] = {
        gauss_make(1, 0),
        gauss_make(0, 1),
        gauss_make(-1, 0),
        gauss_make(0, -1)
    };
    for (int i = 0; i < 4; ++i) {
        gauss_t cand = gauss_mul(a, units[i]);
        if (cand.re > 0 && cand.im >= 0) {
            return cand;
        }
    }
    return a;
}
