#include <array>
#include <cstdint>
#include <span>

// 256-бітове число як контейнер із 4 машинних слів
struct Uint256 {
    std::array<uint64_t, 4> d{0, 0, 0, 0};

    [[nodiscard]] constexpr uint64_t operator[](size_t idx) const noexcept { return d[idx]; }
    [[nodiscard]] constexpr uint64_t& operator[](size_t idx) noexcept { return d[idx]; }
};

// Віднімання двох 256-бітових чисел з поверненням запозичення
[[nodiscard]] constexpr uint64_t sub256(Uint256& res, const Uint256& a, const Uint256& b) noexcept {
    uint64_t borrow = 0;
    for (size_t i = 0; i < 4; ++i) {
        const auto diff = static_cast<unsigned __int128>(a[i]) - b[i] - borrow;
        res[i] = static_cast<uint64_t>(diff);
        borrow = (diff >> 64) ? 1 : 0;
    }
    return borrow;
}

// 256-бітове множення Монтгомері CIOS
[[nodiscard]] Uint256 mont_mul256_cios(const Uint256& a, const Uint256& b,
                                       const Uint256& n, uint64_t n_prime0) noexcept {
    std::array<uint64_t, 6> t{0};

    for (size_t i = 0; i < 4; ++i) {
        uint64_t carry = 0;
        for (size_t j = 0; j < 4; ++j) {
            const auto prod = static_cast<unsigned __int128>(a[i]) * b[j] + t[j] + carry;
            t[j] = static_cast<uint64_t>(prod);
            carry = static_cast<uint64_t>(prod >> 64);
        }
        const auto sum = static_cast<unsigned __int128>(t[4]) + carry;
        t[4] = static_cast<uint64_t>(sum);
        t[5] += static_cast<uint64_t>(sum >> 64);

        const uint64_t m = t[0] * n_prime0;

        auto prod_n = static_cast<unsigned __int128>(m) * n[0] + t[0];
        carry = static_cast<uint64_t>(prod_n >> 64);

        for (size_t j = 1; j < 4; ++j) {
            prod_n = static_cast<unsigned __int128>(m) * n[j] + t[j] + carry;
            t[j - 1] = static_cast<uint64_t>(prod_n);
            carry = static_cast<uint64_t>(prod_n >> 64);
        }

        const auto sum_top = static_cast<unsigned __int128>(t[4]) + carry;
        t[3] = static_cast<uint64_t>(sum_top);
        t[4] = t[5] + static_cast<uint64_t>(sum_top >> 64);
        t[5] = 0;
    }

    Uint256 temp{{t[0], t[1], t[2], t[3]}};
    Uint256 sub_res{};
    const uint64_t borrow = sub256(sub_res, temp, n);

    const uint64_t take_sub = (t[4] != 0) || (borrow == 0);
    const uint64_t mask = -take_sub;

    Uint256 res{};
    for (size_t i = 0; i < 4; ++i) {
        res[i] = (sub_res[i] & mask) | (temp[i] & ~mask);
    }
    return res;
}
