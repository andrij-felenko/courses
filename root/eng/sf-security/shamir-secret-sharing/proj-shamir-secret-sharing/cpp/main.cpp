#include <iostream>
#include <vector>
#include <array>
#include <random>
#include <stdexcept>
#include <span>
#include <cstdint>

class GaloisField256 {
private:
    static constexpr uint16_t GF_POLY = 0x11B;
    std::array<uint8_t, 512> exp_table{};
    std::array<uint8_t, 256> log_table{};

    GaloisField256() {
        uint8_t x = 1;
        for (int i = 0; i < 255; ++i) {
            exp_table[i] = x;
            log_table[x] = static_cast<uint8_t>(i);
            uint16_t x2 = static_cast<uint16_t>(x << 1);
            if (x2 & 0x100) x2 ^= GF_POLY;
            x ^= static_cast<uint8_t>(x2);
        }
        for (int i = 255; i < 512; ++i) {
            exp_table[i] = exp_table[i - 255];
        }
        log_table[0] = 0;
    }

public:
    static const GaloisField256& instance() {
        static GaloisField256 instance;
        return instance;
    }

    [[nodiscard]] uint8_t multiply(uint8_t a, uint8_t b) const noexcept {
        if (a == 0 || b == 0) return 0;
        return exp_table[log_table[a] + log_table[b]];
    }

    [[nodiscard]] uint8_t divide(uint8_t a, uint8_t b) const {
        if (b == 0) throw std::invalid_argument("Ділення на нуль у GF(256)");
        if (a == 0) return 0;
        return exp_table[log_table[a] - log_table[b] + 255];
    }
};

struct Share {
    uint8_t x{0};
    std::vector<uint8_t> data;
};

class ShamirSecretSharing {
public:
    static std::vector<Share> split(std::span<const uint8_t> secret, size_t k, size_t n) {
        if (k < 1 || k > n || n >= 256) {
            throw std::invalid_argument("Некоректні параметри порогу (k, n)");
        }

        const auto& gf = GaloisField256::instance();
        std::vector<Share> shares(n);
        for (size_t i = 0; i < n; ++i) {
            shares[i].x = static_cast<uint8_t>(i + 1);
            shares[i].data.resize(secret.size());
        }

        std::random_device rd;
        std::mt19937 rng(rd());
        std::uniform_int_distribution<int> dist(0, 255);

        std::vector<uint8_t> coeffs(k);

        for (size_t byte_idx = 0; byte_idx < secret.size(); ++byte_idx) {
            coeffs[0] = secret[byte_idx];
            for (size_t c = 1; c < k; ++c) {
                coeffs[c] = static_cast<uint8_t>(dist(rng));
            }

            for (size_t i = 0; i < n; ++i) {
                uint8_t x_val = shares[i].x;
                uint8_t y_val = coeffs[0];
                uint8_t x_pow = 1;

                for (size_t c = 1; c < k; ++c) {
                    x_pow = gf.multiply(x_pow, x_val);
                    y_val ^= gf.multiply(coeffs[c], x_pow);
                }
                shares[i].data[byte_idx] = y_val;
            }
        }

        return shares;
    }

    static std::vector<uint8_t> reconstruct(std::span<const Share> selected_shares, size_t k) {
        if (selected_shares.size() < k || k < 1) {
            throw std::invalid_argument("Недостатня кількість часток для відновлення");
        }

        const auto& gf = GaloisField256::instance();
        const size_t secret_len = selected_shares[0].data.size();
        std::vector<uint8_t> secret(secret_len, 0);

        for (size_t byte_idx = 0; byte_idx < secret_len; ++byte_idx) {
            uint8_t reconstructed_byte = 0;

            for (size_t i = 0; i < k; ++i) {
                uint8_t xi = selected_shares[i].x;
                uint8_t yi = selected_shares[i].data[byte_idx];

                uint8_t li_0 = 1;
                for (size_t j = 0; j < k; ++j) {
                    if (i == j) continue;
                    uint8_t xj = selected_shares[j].x;
                    uint8_t num = xj;
                    uint8_t den = xj ^ xi;
                    li_0 = gf.multiply(li_0, gf.divide(num, den));
                }
                reconstructed_byte ^= gf.multiply(yi, li_0);
            }
            secret[byte_idx] = reconstructed_byte;
        }

        return secret;
    }
};
