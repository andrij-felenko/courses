#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <array>
#include <algorithm>
#include <stdexcept>
#include <expected>

namespace ceremony {

class GaloisField256 {
public:
    constexpr GaloisField256() noexcept {
        init();
    }

    [[nodiscard]] uint8_t mul(uint8_t a, uint8_t b) const noexcept {
        if (a == 0 || b == 0) return 0;
        return exp_[log_[a] + log_[b]];
    }

    [[nodiscard]] uint8_t div(uint8_t a, uint8_t b) const {
        if (b == 0) throw std::invalid_argument("Ділення на нуль у GF(256)");
        if (a == 0) return 0;
        return exp_[(log_[a] + 255 - log_[b]) % 255];
    }

private:
    std::array<uint8_t, 512> exp_{};
    std::array<uint8_t, 256> log_{};

    void init() noexcept {
        uint32_t val = 1;
        for (int i = 0; i < 255; ++i) {
            exp_[i] = static_cast<uint8_t>(val);
            exp_[i + 255] = static_cast<uint8_t>(val);
            log_[val] = static_cast<uint8_t>(i);
            val <<= 1;
            if (val & 0x100) {
                val ^= 0x11B; // x^8 + x^4 + x^3 + x + 1
            }
        }
        log_[0] = 0;
    }
};

static const GaloisField256 gf{};

/* Структура частки із захищеним очищенням деструктором RAII */
struct SecretShare {
    uint8_t index{0};
    std::vector<uint8_t> data{};

    ~SecretShare() {
        std::ranges::fill(data, 0);
    }

    SecretShare() = default;
    SecretShare(uint8_t idx, std::vector<uint8_t> bytes)
        : index(idx), data(std::move(bytes)) {}
    SecretShare(const SecretShare&) = default;
    SecretShare& operator=(const SecretShare&) = default;
    SecretShare(SecretShare&&) noexcept = default;
    SecretShare& operator=(SecretShare&&) noexcept = default;
};

enum class SplitError {
    InvalidThreshold,
    InsufficientRandomBytes,
    SecretEmpty
};

enum class CombineError {
    InsufficientShares,
    DuplicateIndices,
    InconsistentShareLengths
};

/* Розщеплення секрету на n часток із порогом k */
std::expected<std::vector<SecretShare>, SplitError>
split_secret(std::span<const uint8_t> secret,
             uint8_t k, uint8_t n,
             std::span<const uint8_t> random_bytes) {
    if (k < 2 || k > n) return std::unexpected(SplitError::InvalidThreshold);
    if (secret.empty()) return std::unexpected(SplitError::SecretEmpty);
    if (random_bytes.size() < static_cast<size_t>(k - 1) * secret.size()) {
        return std::unexpected(SplitError::InsufficientRandomBytes);
    }

    std::vector<SecretShare> shares;
    shares.reserve(n);
    for (uint8_t i = 1; i <= n; ++i) {
        shares.emplace_back(i, std::vector<uint8_t>(secret.size(), 0));
    }

    for (size_t byte_idx = 0; byte_idx < secret.size(); ++byte_idx) {
        const uint8_t s_byte = secret[byte_idx];
        
        for (auto& share : shares) {
            uint8_t x = share.index;
            uint8_t y = s_byte;
            uint8_t x_pow = x;

            for (uint8_t deg = 1; deg < k; ++deg) {
                uint8_t coef = random_bytes[(deg - 1) * secret.size() + byte_idx];
                y ^= gf.mul(coef, x_pow);
                x_pow = gf.mul(x_pow, x);
            }
            share.data[byte_idx] = y;
        }
    }
    return shares;
}

/* Відновлення секрету за наданими частками */
std::expected<std::vector<uint8_t>, CombineError>
combine_shares(std::span<const SecretShare> shares, uint8_t k) {
    if (shares.size() < k || k < 2) {
        return std::unexpected(CombineError::InsufficientShares);
    }

    const size_t len = shares[0].data.size();
    for (const auto& sh : shares) {
        if (sh.data.size() != len) return std::unexpected(CombineError::InconsistentShareLengths);
    }

    // Перевірка унікальності індексів
    for (size_t i = 0; i < k; ++i) {
        for (size_t j = i + 1; j < k; ++j) {
            if (shares[i].index == shares[j].index) {
                return std::unexpected(CombineError::DuplicateIndices);
            }
        }
    }

    // Ваги Лагранжа
    std::vector<uint8_t> lagrange_weights(k);
    for (size_t j = 0; j < k; ++j) {
        uint8_t num = 1;
        uint8_t den = 1;
        uint8_t xj = shares[j].index;

        for (size_t m = 0; m < k; ++m) {
            if (m == j) continue;
            uint8_t xm = shares[m].index;
            num = gf.mul(num, xm);
            den = gf.mul(den, xj ^ xm);
        }
        lagrange_weights[j] = gf.div(num, den);
    }

    std::vector<uint8_t> recovered(len, 0);
    for (size_t byte_idx = 0; byte_idx < len; ++byte_idx) {
        uint8_t s = 0;
        for (size_t j = 0; j < k; ++j) {
            s ^= gf.mul(shares[j].data[byte_idx], lagrange_weights[j]);
        }
        recovered[byte_idx] = s;
    }
    return recovered;
}

} // namespace ceremony
