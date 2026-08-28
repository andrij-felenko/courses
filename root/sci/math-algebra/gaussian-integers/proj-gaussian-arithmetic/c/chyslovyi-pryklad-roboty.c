/* Швидке модульне піднесення до степеня: (base^exp) % mod із захистом від переповнення */
static uint64_t mod_pow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            res = (uint64_t)((__int128)res * base % mod);
        }
        base = (uint64_t)((__int128)base * base % mod);
        exp >>= 1;
    }
    return res;
}

/* Пошук z, такого що z^2 = -1 (mod p) для p = 1 (mod 4) */
static int64_t find_sqrt_minus_one(uint64_t p) {
    if (p % 4 != 1) return -1;
    /* Шукаємо перший квадратичний нелишок g */
    uint64_t g = 2;
    while (mod_pow(g, (p - 1) / 2, p) != p - 1) {
        g++;
    }
    /* z = g^((p - 1) / 4) mod p */
    return (int64_t)mod_pow(g, (p - 1) / 4, p);
}

/* Розклад простого числа p = a^2 + b^2 через алгоритм Корначчі — Евкліда в ℤ[i] */
bool solve_sum_of_two_squares(uint64_t p, int64_t* out_a, int64_t* out_b) {
    if (p == 2) {
        *out_a = 1;
        *out_b = 1;
        return true;
    }
    if (p % 4 != 1) {
        return false; /* За теоремою Ферма числа 4k + 3 не представляються сумою двох квадратів */
    }

    int64_t z = find_sqrt_minus_one(p);
    if (z < 0) return false;

    /* Обчислюємо gcd(p, z + i) в кільці гауссових цілих чисел */
    gauss_t p_gauss = gauss_make((int64_t)p, 0);
    gauss_t z_gauss = gauss_make(z, 1);
    gauss_t g = gauss_gcd(p_gauss, z_gauss);

    g = gauss_canonical(g);
    *out_a = llabs(g.re);
    *out_b = llabs(g.im);
    return true;
}
