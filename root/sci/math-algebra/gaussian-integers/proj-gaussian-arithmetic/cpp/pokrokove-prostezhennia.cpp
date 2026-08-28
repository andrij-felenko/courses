template <std::integral T>
constexpr T round_division(T num, T den) noexcept {
    if (den < 0) {
        num = -num;
        den = -den;
    }
    return (num >= 0) ? (num + den / 2) / den : (num - den / 2) / den;
}

template <std::integral T = int64_t>
struct GaussianDivResult {
    GaussianInteger<T> quotient;
    GaussianInteger<T> remainder;
};

/* Ділення з остачею в кільці ℤ[i] */
template <std::integral T>
GaussianDivResult<T> divide_with_remainder(const GaussianInteger<T>& a, const GaussianInteger<T>& b) {
    const uint64_t den = b.norm();
    if (den == 0) {
        throw std::domain_error("Division by zero in Gaussian integer ring");
    }

    const T num_re = a.re * b.re + a.im * b.im;
    const T num_im = a.im * b.re - a.re * b.im;

    const T q_re = round_division(num_re, static_cast<T>(den));
    const T q_im = round_division(num_im, static_cast<T>(den));

    const GaussianInteger<T> q{q_re, q_im};
    const GaussianInteger<T> r = a - q * b;
    return {q, r};
}

/* Алгоритм Евкліда для пошуку НСД у ℤ[i] */
template <std::integral T>
GaussianInteger<T> gcd(GaussianInteger<T> a, GaussianInteger<T> b) noexcept {
    while (!b.is_zero()) {
        auto [q, r] = divide_with_remainder(a, b);
        a = b;
        b = r;
    }
    return a;
}

/* Нормалізація до канонічного представника (re > 0, im >= 0) */
template <std::integral T>
GaussianInteger<T> to_primary_associate(const GaussianInteger<T>& z) noexcept {
    if (z.is_zero()) return z;
    const GaussianInteger<T> units[4] = {
        {1, 0}, {0, 1}, {-1, 0}, {0, -1}
    };
    for (const auto& u : units) {
        GaussianInteger<T> cand = z * u;
        if (cand.re > 0 && cand.im >= 0) {
            return cand;
        }
    }
    return z;
}
