// ldpc_decoder.hpp — Ідіоматична C++20 реалізація Min-Sum декодера
#pragma once
#include <vector>
#include <span>
#include <optional>
#include <cmath>
#include <limits>
#include <cstdint>
#include <memory>

namespace coding {

class LdpcDecoder {
public:
    struct Config {
        std::size_t num_v;
        std::size_t num_c;
        std::vector<std::int32_t> h_matrix; // 1D плоска матриця (num_c x num_v)
    };

    explicit LdpcDecoder(const Config& config) 
        : num_v_(config.num_v), num_c_(config.num_c) {
        
        cn_adj_.resize(num_c_);
        vn_adj_.resize(num_v_);

        std::size_t edge_counter = 0;
        for (std::size_t i = 0; i < num_c_; ++i) {
            for (std::size_t j = 0; j < num_v_; ++j) {
                if (config.h_matrix[i * num_v_ + j] != 0) {
                    std::size_t e = edge_counter++;
                    cn_adj_[i].push_back({j, e});
                    vn_adj_[j].push_back({i, e});
                }
            }
        }

        num_edges_ = edge_counter;
        msg_v2c_.resize(num_edges_, 0.0f);
        msg_c2v_.resize(num_edges_, 0.0f);
    }

    // RAII автоматично звільняє ресурси контейнерів
    ~LdpcDecoder() = default;

    [[nodiscard]] std::optional<std::vector<std::uint8_t>> decode(
        std::span<const float> channel_llr,
        std::size_t max_iterations = 50,
        float norm_factor = 0.8f) 
    {
        if (channel_llr.size() != num_v_) {
            return std::nullopt;
        }

        // Крок 1: Ініціалізація повідомлень
        for (std::size_t j = 0; j < num_v_; ++j) {
            for (const auto& edge : vn_adj_[j]) {
                msg_v2c_[edge.edge_idx] = channel_llr[j];
            }
        }

        std::vector<std::uint8_t> decoded_bits(num_v_);

        for (std::size_t iter = 0; iter < max_iterations; ++iter) {
            // Крок 2: Фаза Перевірочних Вузлів (CN -> VN)
            for (std::size_t i = 0; i < num_c_; ++i) {
                const auto& edges = cn_adj_[i];
                const std::size_t deg = edges.size();

                for (std::size_t k = 0; k < deg; ++k) {
                    float min_val = std::numeric_limits<float>::max();
                    int sign_prod = 1;

                    for (std::size_t m = 0; m < deg; ++m) {
                        if (m == k) continue;
                        float val = msg_v2c_[edges[m].edge_idx];
                        if (val < 0.0f) sign_prod = -sign_prod;
                        min_val = std::min(min_val, std::abs(val));
                    }

                    msg_c2v_[edges[k].edge_idx] = norm_factor * static_cast<float>(sign_prod) * min_val;
                }
            }

            // Крок 3: Фаза Символьних Вузлів (VN -> CN) та формування рішення
            for (std::size_t j = 0; j < num_v_; ++j) {
                float total_llr = channel_llr[j];
                for (const auto& edge : vn_adj_[j]) {
                    total_llr += msg_c2v_[edge.edge_idx];
                }

                decoded_bits[j] = (total_llr < 0.0f) ? 1 : 0;

                for (const auto& edge : vn_adj_[j]) {
                    msg_v2c_[edge.edge_idx] = total_llr - msg_c2v_[edge.edge_idx];
                }
            }

            // Крок 4: Перевірка синдрому
            if (check_syndrome(decoded_bits)) {
                return decoded_bits; // Успіх
            }
        }

        return std::nullopt; // Перевищено ліміт ітерацій
    }

private:
    struct EdgeInfo {
        std::size_t node_idx;
        std::size_t edge_idx;
    };

    [[nodiscard]] bool check_syndrome(std::span<const std::uint8_t> bits) const {
        for (std::size_t i = 0; i < num_c_; ++i) {
            std::uint8_t sum = 0;
            for (const auto& edge : cn_adj_[i]) {
                sum ^= bits[edge.node_idx];
            }
            if (sum != 0) return false;
        }
        return true;
    }

    std::size_t num_v_;
    std::size_t num_c_;
    std::size_t num_edges_{0};

    std::vector<std::vector<EdgeInfo>> cn_adj_;
    std::vector<std::vector<EdgeInfo>> vn_adj_;

    std::vector<float> msg_v2c_;
    std::vector<float> msg_c2v_;
};

} // namespace coding
