#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <array>
#include <algorithm>
#include <stdexcept>

namespace bignum {

class MontgomeryEngine {
public:
    static constexpr uint64_t compute_n0_prime(uint64_t n0) noexcept {
        uint64_t inv = 1;
        for (int i = 0; i < 6; ++i) {
            inv = inv * (2 - n0 * inv);
        }
        return static_cast<uint64_t>(-static_cast<int64_t>(inv));
    }

    static void multiply_cios(std::span<const uint64_t> a,
                              std::span<const uint64_t> b,
                              std::span<const uint64_t> n,
                              uint64_t n0_prime,
                              std::span<uint64_t> res) {
        const size_t k = n.size();
        if (a.size() != k || b.size() != k || res.size() != k) {
            throw std::invalid_argument("Montgomery multiplication operands size mismatch");
        }

        std::vector<uint64_t> t(k + 2, 0);

        for (size_t i = 0; i < k; ++i) {
            uint64_t carry = 0;
            for (size_t j = 0; j < k; ++j) {
                __uint128_t prod = static_cast<__uint128_t>(a[i]) * b[j] + t[j] + carry;
                t[j] = static_cast<uint64_t>(prod);
                carry = static_cast<uint64_t>(prod >> 64);
            }
            __uint128_t sum_carry = static_cast<__uint128_t>(t[k]) + carry;
            t[k] = static_cast<uint64_t>(sum_carry);
            t[k + 1] = static_cast<uint64_t>(sum_carry >> 64);

            uint64_t m = static_cast<uint64_t>(t[0] * n0_prime);

            __uint128_t prod_m0 = static_cast<__uint128_t>(m) * n[0] + t[0];
            uint64_t c2 = static_cast<uint64_t>(prod_m0 >> 64);

            for (size_t j = 1; j < k; ++j) {
                __uint128_t prod = static_cast<__uint128_t>(m) * n[j] + t[j] + c2;
                t[j - 1] = static_cast<uint64_t>(prod);
                c2 = static_cast<uint64_t>(prod >> 64);
            }

            __uint128_t sum2 = static_cast<__uint128_t>(t[k]) + c2;
            t[k - 1] = static_cast<uint64_t>(sum2);
            t[k] = t[k + 1] + static_cast<uint64_t>(sum2 >> 64);
            t[k + 1] = 0;
        }

        std::copy_n(t.begin(), k, res.begin());
        sub_conditional_constant_time(res, n);
    }

private:
    static void sub_conditional_constant_time(std::span<uint64_t> u,
                                              std::span<const uint64_t> n) noexcept {
        const size_t k = n.size();
        uint64_t borrow = 0;
        std::vector<uint64_t> diff(k);

        for (size_t i = 0; i < k; ++i) {
            __uint128_t sub = static_cast<__uint128_t>(u[i]) - n[i] - borrow;
            diff[i] = static_cast<uint64_t>(sub);
            borrow = static_cast<uint64_t>(sub >> 127) & 1;
        }

        const uint64_t mask = static_cast<uint64_t>(-static_cast<int64_t>(1 - borrow));
        for (size_t i = 0; i < k; ++i) {
            u[i] = (diff[i] & mask) | (u[i] & ~mask);
        }
    }
};

} // namespace bignum
