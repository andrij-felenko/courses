#include <vector>
#include <span>
#include <array>
#include <cstdint>

struct Monomial {
    int64_t coeff{0};
    std::array<uint8_t, 8> exponents{};
};

class SparsePolynomial {
public:
    explicit SparsePolynomial(std::size_t num_vars, std::vector<Monomial> terms)
        : num_vars_(num_vars), terms_(std::move(terms)) {}

    [[nodiscard]] int64_t evaluate(std::span<const int64_t> v) const noexcept {
        int64_t total = 0;
        for (const auto& term : terms_) {
            int64_t term_val = term.coeff;
            for (std::size_t i = 0; i < num_vars_; ++i) {
                for (uint8_t e = 0; e < term.exponents[i]; ++e) {
                    term_val *= v[i];
                }
            }
            total += term_val;
        }
        return total;
    }

private:
    std::size_t num_vars_;
    std::vector<Monomial> terms_;
};
