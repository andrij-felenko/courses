/* Запис одного простого множника та його показника степеня */
typedef struct {
    gauss_t prime;
    int power;
} prime_factor_t;

/* Структура повного розкладу гауссового числа */
typedef struct {
    gauss_t unit;               /* оборотна одиниця {1, i, -1, -i} */
    int count;                  /* кількість різних простих множників */
    prime_factor_t factors[32]; /* масив множників */
} gauss_factorization_t;

/* Перевірка подільності націло в ℤ[i] */
static bool gauss_divides(gauss_t d, gauss_t n) {
    if (gauss_is_zero(d)) return false;
    gauss_div_t res = gauss_div_rem(n, d);
    return gauss_is_zero(res.r);
}

/* Повна факторизація гауссового числа α */
gauss_factorization_t gauss_factorize(gauss_t alpha) {
    gauss_factorization_t fact;
    fact.count = 0;
    fact.unit = gauss_make(1, 0);

    if (gauss_is_zero(alpha) || gauss_is_unit(alpha)) {
        fact.unit = alpha;
        return fact;
    }

    gauss_t curr = alpha;

    /* 1. Виділяємо дільники 1 + i */
    gauss_t one_plus_i = gauss_make(1, 1);
    int p2_count = 0;
    while (gauss_divides(one_plus_i, curr)) {
        p2_count++;
        curr = gauss_div_rem(curr, one_plus_i).q;
    }
    if (p2_count > 0) {
        fact.factors[fact.count].prime = one_plus_i;
        fact.factors[fact.count].power = p2_count;
        fact.count++;
    }

    /* 2. Перебираємо непарні дільники норми */
    uint64_t norm = gauss_norm(curr);
    for (uint64_t d = 3; d * d <= norm; d += 2) {
        if (norm % d != 0) continue;

        /* Перевірка простоти числа d */
        bool is_prime = true;
        for (uint64_t k = 3; k * k <= d; k += 2) {
            if (d % k == 0) { is_prime = false; break; }
        }
        if (!is_prime) continue;

        if (d % 4 == 3) {
            /* Інертне просте число */
            gauss_t p_inert = gauss_make((int64_t)d, 0);
            int inert_power = 0;
            while (gauss_divides(p_inert, curr)) {
                inert_power++;
                curr = gauss_div_rem(curr, p_inert).q;
            }
            if (inert_power > 0) {
                fact.factors[fact.count].prime = p_inert;
                fact.factors[fact.count].power = inert_power;
                fact.count++;
            }
        } else if (d % 4 == 1) {
            /* Розщеплене просте число d = a^2 + b^2 */
            int64_t a, b;
            solve_sum_of_two_squares(d, &a, &b);
            gauss_t pi1 = gauss_canonical(gauss_make(a, b));
            gauss_t pi2 = gauss_canonical(gauss_make(a, -b));

            int count1 = 0;
            while (gauss_divides(pi1, curr)) {
                count1++;
                curr = gauss_div_rem(curr, pi1).q;
            }
            if (count1 > 0) {
                fact.factors[fact.count].prime = pi1;
                fact.factors[fact.count].power = count1;
                fact.count++;
            }

            int count2 = 0;
            while (gauss_divides(pi2, curr)) {
                count2++;
                curr = gauss_div_rem(curr, pi2).q;
            }
            if (count2 > 0) {
                fact.factors[fact.count].prime = pi2;
                fact.factors[fact.count].power = count2;
                fact.count++;
            }
        }
        norm = gauss_norm(curr);
    }

    /* Залишковий множник, якщо він більший за 1 */
    if (!gauss_is_unit(curr)) {
        fact.factors[fact.count].prime = gauss_canonical(curr);
        fact.factors[fact.count].power = 1;
        fact.count++;
        curr = gauss_make(1, 0);
    }

    fact.unit = curr;
    return fact;
}
