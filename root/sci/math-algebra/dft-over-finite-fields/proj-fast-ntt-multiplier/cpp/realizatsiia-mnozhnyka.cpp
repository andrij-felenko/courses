#include <iostream>
#include <vector>
#include <span>
#include <cstdint>
#include <stdexcept>
#include <numeric>

namespace ntt {

/* Параметри поля Галуа GF(65537) */
constexpr uint64_t MODULUS = 65537ULL;
constexpr uint64_t MONT_R2  = 1ULL;
constexpr uint64_t P_INV    = 4294901759ULL; // -p^(-1) mod 2^32

/* Клас елемента поля у формі Монтгомері (RAII та безпечна арифметика) */
class MontgomeryElement {
public:
    uint32_t val;

    constexpr MontgomeryElement() : val(0) {}
    explicit constexpr MontgomeryElement(uint32_t raw_val, bool in_mont = false) {
        val = in_mont ? raw_val : to_mont(raw_val);
    }

    static constexpr uint32_t reduce(uint64_t T) noexcept {
        uint64_t m = static_cast<uint32_t>(static_cast<uint32_t>(T) * static_cast<uint32_t>(P_INV));
        uint64_t t = (T + m * MODULUS) >> 32;
        return static_cast<uint32_t>((t >= MODULUS) ? (t - MODULUS) : t);
    }

    static constexpr uint32_t to_mont(uint32_t x) noexcept {
        return reduce(static_cast<uint64_t>(x) * MONT_R2);
    }

    [[nodiscard]] constexpr uint32_t get_raw() const noexcept {
        return reduce(static_cast<uint64_t>(val));
    }

    constexpr MontgomeryElement operator+(const MontgomeryElement& rhs) const noexcept {
        uint32_t sum = val + rhs.val;
        return MontgomeryElement((sum >= MODULUS) ? (sum - MODULUS) : sum, true);
    }

    constexpr MontgomeryElement operator-(const MontgomeryElement& rhs) const noexcept {
        uint32_t diff = (val >= rhs.val) ? (val - rhs.val) : (val + MODULUS - rhs.val);
        return MontgomeryElement(diff, true);
    }

    constexpr MontgomeryElement operator*(const MontgomeryElement& rhs) const noexcept {
        return MontgomeryElement(reduce(static_cast<uint64_t>(val) * rhs.val), true);
    }
};

/* Обчислення степеня числа за модулем у compile-time або runtime */
constexpr uint32_t power_mod(uint32_t base, uint32_t exp, uint32_t mod) noexcept {
    uint64_t res = 1;
    uint64_t b = base % mod;
    while (exp > 0) {
        if (exp & 1) res = (res * b) % mod;
        b = (b * b) % mod;
        exp >>= 1;
    }
    return static_cast<uint32_t>(res);
}

/* Отримання кореня з одиниці степеня n */
inline MontgomeryElement get_primitive_root(uint32_t n) {
    constexpr uint32_t G = 3;
    uint32_t exp = (MODULUS - 1) / n;
    return MontgomeryElement(power_mod(G, exp, MODULUS));
}

/* Таблиця поворотних коефіцієнтів */
struct TwiddleTables {
    std::vector<MontgomeryElement> twiddles;
    std::vector<MontgomeryElement> inv_twiddles;

    explicit TwiddleTables(size_t n) : twiddles(n), inv_twiddles(n) {
        auto root = get_primitive_root(static_cast<uint32_t>(n));
        auto inv_root = MontgomeryElement(power_mod(root.get_raw(), MODULUS - 2, MODULUS));

        size_t idx = 1;
        for (size_t len = n >> 1; len > 0; len >>= 1) {
            MontgomeryElement cur(1);
            MontgomeryElement cur_inv(1);
            uint32_t step_raw = power_mod(root.get_raw(), (MODULUS - 1) / (n / len), MODULUS);
            uint32_t step_inv_raw = power_mod(inv_root.get_raw(), (MODULUS - 1) / (n / len), MODULUS);
            MontgomeryElement step(step_raw);
            MontgomeryElement step_inv(step_inv_raw);

            for (size_t j = 0; j < (n / (len << 1)); ++j) {
                twiddles[idx] = cur;
                inv_twiddles[idx] = cur_inv;
                ++idx;
                cur = cur * step;
                cur_inv = cur_inv * step_inv;
            }
        }
    }
};

/* Прямий NTT: DIF метелик (природний порядок -> інверсно-бітовий) */
void ntt_dif(std::span<MontgomeryElement> a, const std::vector<MontgomeryElement>& tw) {
    const size_t n = a.size();
    size_t t = n >> 1;
    size_t tw_idx = 1;
    while (t > 0) {
        for (size_t i = 0; i < n; i += (t << 1)) {
            const auto w = tw[tw_idx++];
            for (size_t j = i; j < i + t; ++j) {
                const auto u = a[j];
                const auto v = a[j + t];
                a[j] = u + v;
                a[j + t] = (u - v) * w;
            }
        }
        t >>= 1;
    }
}

/* Обернений INTT: DIT метелик (інверсно-бітовий -> природний) */
void intt_dit(std::span<MontgomeryElement> a, const std::vector<MontgomeryElement>& inv_tw) {
    const size_t n = a.size();
    size_t t = 1;
    size_t tw_idx = 1;
    while (t < n) {
        for (size_t i = 0; i < n; i += (t << 1)) {
            const auto w = inv_tw[tw_idx++];
            for (size_t j = i; j < i + t; ++j) {
                const auto u = a[j];
                const auto v = a[j + t] * w;
                a[j] = u + v;
                a[j + t] = u - v;
            }
        }
        t <<= 1;
    }
    /* Множення на 1/n */
    MontgomeryElement n_inv(power_mod(static_cast<uint32_t>(n), MODULUS - 2, MODULUS));
    for (auto& elem : a) {
        elem = elem * n_inv;
    }
}

/* Множення многочленів через поліморфний інтерфейс std::span */
[[nodiscard]] std::vector<uint32_t> multiply_polynomials(
    std::span<const uint32_t> poly_a,
    std::span<const uint32_t> poly_b) 
{
    if (poly_a.empty() || poly_b.empty()) return {};

    size_t result_len = poly_a.size() + poly_b.size() - 1;
    size_t n = 1;
    while (n < result_len) n <<= 1;

    std::vector<MontgomeryElement> a(n), b(n);
    for (size_t i = 0; i < poly_a.size(); ++i) a[i] = MontgomeryElement(poly_a[i]);
    for (size_t i = 0; i < poly_b.size(); ++i) b[i] = MontgomeryElement(poly_b[i]);

    TwiddleTables tables(n);

    /* Пряме перетворення */
    ntt_dif(a, tables.twiddles);
    ntt_dif(b, tables.twiddles);

    /* Поточкове спектральне множення */
    for (size_t i = 0; i < n; ++i) {
        a[i] = a[i] * b[i];
    }

    /* Обернене перетворення */
    intt_dit(a, tables.inv_twiddles);

    /* Формування результуючого вектора */
    std::vector<uint32_t> result(result_len);
    for (size_t i = 0; i < result_len; ++i) {
        result[i] = a[i].get_raw();
    }
    return result;
}

} // namespace ntt
