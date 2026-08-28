#include <random>
#include <memory>
#include <cstdint>

// Оптимізований C++ клас генерації MinHash сигнатур з генератором Mersenne Twister
class MinHashGenerator {
public:
    struct HashParam {
        uint64_t a;
        uint64_t b;
    };

    explicit MinHashGenerator(size_t k_funcs, uint64_t seed = 42) 
        : k_funcs_(k_funcs), prime_(4294967311ULL) {
        std::mt19937_64 rng(seed);
        std::uniform_int_distribution<uint64_t> dist_a(1, prime_ - 1);
        std::uniform_int_distribution<uint64_t> dist_b(0, prime_ - 1);

        params_.reserve(k_funcs_);
        for (size_t i = 0; i < k_funcs_; ++i) {
            params_.push_back({dist_a(rng), dist_b(rng)});
        }
    }

    [[nodiscard]] std::vector<uint64_t> compute(std::span<const uint64_t> shingles) const {
        std::vector<uint64_t> sig(k_funcs_, UINT64_MAX);
        for (size_t i = 0; i < k_funcs_; ++i) {
            const auto& [a, b] = params_[i];
            for (uint64_t item : shingles) {
                uint64_t h = (a * item + b) % prime_;
                if (h < sig[i]) sig[i] = h;
            }
        }
        return sig;
    }

    static double similarity(std::span<const uint64_t> sig_a, std::span<const uint64_t> sig_b) {
        if (sig_a.size() != sig_b.size() || sig_a.empty()) return 0.0;
        size_t matches = 0;
        for (size_t i = 0; i < sig_a.size(); ++i) {
            if (sig_a[i] == sig_b[i]) matches++;
        }
        return static_cast<double>(matches) / static_cast<double>(sig_a.size());
    }

private:
    size_t k_funcs_;
    uint64_t prime_;
    std::vector<HashParam> params_;
};
