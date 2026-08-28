/* Модульне піднесення до степеня з використанням 128-бітного проміжного типу */
constexpr uint64_t modular_exponentiation(uint64_t base, uint64_t exp, uint64_t mod) noexcept {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = static_cast<uint64_t>(static_cast<unsigned __int128>(result) * base % mod);
        }
        base = static_cast<uint64_t>(static_cast<unsigned __int128>(base) * base % mod);
        exp >>= 1;
    }
    return result;
}

/* Пошук кореня рівняння z^2 = -1 (mod p) */
std::optional<uint64_t> modular_sqrt_minus_one(uint64_t p) noexcept {
    if (p % 4 != 1) return std::nullopt;
    uint64_t g = 2;
    while (modular_exponentiation(g, (p - 1) / 2, p) != p - 1) {
        g++;
    }
    return modular_exponentiation(g, (p - 1) / 4, p);
}

/* Алгоритм Корначчі: розклад p = a^2 + b^2 через НСД у ℤ[i] */
std::optional<std::pair<int64_t, int64_t>> find_sum_of_two_squares(uint64_t p) {
    if (p == 2) return std::make_pair(1LL, 1LL);
    if (p % 4 != 1) return std::nullopt;

    auto z_opt = modular_sqrt_minus_one(p);
    if (!z_opt) return std::nullopt;

    const GaussianInteger<int64_t> p_gauss{static_cast<int64_t>(p), 0};
    const GaussianInteger<int64_t> z_gauss{static_cast<int64_t>(*z_opt), 1};

    const GaussianInteger<int64_t> g = to_primary_associate(gcd(p_gauss, z_gauss));
    return std::make_pair(std::abs(g.re), std::abs(g.im));
}
