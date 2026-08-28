template <std::integral T = int64_t>
struct GaussianFactorization {
    GaussianInteger<T> unit{1, 0};
    std::vector<std::pair<GaussianInteger<T>, int>> factors;
};

/* Перевірка подільності в кільці ℤ[i] */
template <std::integral T>
bool divides(const GaussianInteger<T>& divisor, const GaussianInteger<T>& target) noexcept {
    if (divisor.is_zero()) return false;
    auto [q, r] = divide_with_remainder(target, divisor);
    return r.is_zero();
}

/* Повна факторизація гауссового числа */
template <std::integral T = int64_t>
GaussianFactorization<T> factorize(GaussianInteger<T> z) {
    GaussianFactorization<T> result;
    if (z.is_zero() || z.is_unit()) {
        result.unit = z;
        return result;
    }

    GaussianInteger<T> curr = z;

    /* 1. Факторизація розгалуженої двійки (1 + i) */
    const GaussianInteger<T> one_plus_i{1, 1};
    int count_2 = 0;
    while (divides(one_plus_i, curr)) {
        count_2++;
        curr = divide_with_remainder(curr, one_plus_i).quotient;
    }
    if (count_2 > 0) {
        result.factors.emplace_back(one_plus_i, count_2);
    }

    /* 2. Поділ на непарні прості числа за нормою */
    uint64_t norm = curr.norm();
    for (uint64_t d = 3; d * d <= norm; d += 2) {
        if (norm % d != 0) continue;

        bool is_prime = true;
        for (uint64_t k = 3; k * k <= d; k += 2) {
            if (d % k == 0) { is_prime = false; break; }
        }
        if (!is_prime) continue;

        if (d % 4 == 3) {
            const GaussianInteger<T> p_inert{static_cast<T>(d), 0};
            int power = 0;
            while (divides(p_inert, curr)) {
                power++;
                curr = divide_with_remainder(curr, p_inert).quotient;
            }
            if (power > 0) {
                result.factors.emplace_back(p_inert, power);
            }
        } else if (d % 4 == 1) {
            auto [a, b] = *find_sum_of_two_squares(d);
            const GaussianInteger<T> pi1 = to_primary_associate(GaussianInteger<T>{a, b});
            const GaussianInteger<T> pi2 = to_primary_associate(GaussianInteger<T>{a, -b});

            int cnt1 = 0;
            while (divides(pi1, curr)) {
                cnt1++;
                curr = divide_with_remainder(curr, pi1).quotient;
            }
            if (cnt1 > 0) result.factors.emplace_back(pi1, cnt1);

            int cnt2 = 0;
            while (divides(pi2, curr)) {
                cnt2++;
                curr = divide_with_remainder(curr, pi2).quotient;
            }
            if (cnt2 > 0) result.factors.emplace_back(pi2, cnt2);
        }
        norm = curr.norm();
    }

    if (!curr.is_unit()) {
        result.factors.emplace_back(to_primary_associate(curr), 1);
        curr = {1, 0};
    }

    result.unit = curr;
    return result;
}
