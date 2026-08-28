#include <vector>
#include <cstdint>
#include <memory>
#include <stdexcept>

class LinearSieve {
private:
    std::uint32_t max_n_;
    std::vector<std::uint32_t> primes_;
    std::vector<std::uint32_t> min_prime_;
    std::vector<std::uint64_t> sigma_;
    std::vector<std::uint64_t> sigma_p_;

public:
    explicit LinearSieve(std::uint32_t max_n)
        : max_n_(max_n), min_prime_(max_n + 1, 0),
          sigma_(max_n + 1, 0), sigma_p_(max_n + 1, 0) {
        
        primes_.reserve(max_n / 10);
        sigma_[1] = 1;
        sigma_p_[1] = 1;

        for (std::uint32_t i = 2; i <= max_n_; ++i) {
            if (min_prime_[i] == 0) {
                min_prime_[i] = i;
                primes_.push_back(i);
                sigma_[i] = i + 1;
                sigma_p_[i] = i + 1;
            }

            for (std::uint32_t p : primes_) {
                if (p > min_prime_[i] || static_cast<std::uint64_t>(i) * p > max_n_) {
                    break;
                }

                std::uint32_t target = i * p;
                min_prime_[target] = p;

                if (i % p == 0) {
                    sigma_p_[target] = sieve_p_p(p) + sigma_p_[i] * p - p;
                    sigma_[target] = (sigma_[i] / sigma_p_[i]) * sigma_p_[target];
                    break;
                } else {
                    sigma_p_[target] = p + 1;
                    sigma_[target] = sigma_[i] * sieve_p_p(p);
                }
            }
        }
    }

    [[nodiscard]] std::uint64_t get_sigma(std::uint32_t n) const {
        return sigma_.at(n);
    }

    [[nodiscard]] bool is_abundant(std::uint32_t n) const {
        return n > 1 && sigma_.at(n) > 2 * static_cast<std::uint64_t>(n);
    }

private:
    [[nodiscard]] static constexpr std::uint64_t sieve_p_p(std::uint32_t p) noexcept {
        return static_cast<std::uint64_t>(p) + 1;
    }
};
