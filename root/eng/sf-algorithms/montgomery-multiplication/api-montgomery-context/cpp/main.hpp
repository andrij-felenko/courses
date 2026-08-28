#ifndef MONTGOMERY_CONTEXT_HPP
#define MONTGOMERY_CONTEXT_HPP

#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <stdexcept>
#include <memory>

namespace bignum {

class MontgomeryContext {
public:
    /**
     * @brief Конструктор контексту Монтгомері
     * @param modulus Лімби модуля N (little-endian, модуль має бути непарним)
     * @throws std::invalid_argument якщо модуль парний або порожній
     */
    explicit MontgomeryContext(std::span<const uint64_t> modulus);

    ~MontgomeryContext() noexcept;

    // Заборона копіювання для запобігання дублювання робочих буферів
    MontgomeryContext(const MontgomeryContext&) = delete;
    MontgomeryContext& operator=(const MontgomeryContext&) = delete;

    // Дозвіл переміщення
    MontgomeryContext(MontgomeryContext&&) noexcept = default;
    MontgomeryContext& operator=(MontgomeryContext&&) noexcept = default;

    [[nodiscard]] size_t limb_count() const noexcept { return k_; }
    [[nodiscard]] uint64_t n0_prime() const noexcept { return n0_prime_; }
    [[nodiscard]] std::span<const uint64_t> modulus() const noexcept { return n_; }

    /**
     * @brief Переведення у простір Монтгомері
     */
    void to_domain(std::span<const uint64_t> a, std::span<uint64_t> a_bar) const;

    /**
     * @brief Зворотне переведення зі простору Монтгомері
     */
    void from_domain(std::span<const uint64_t> a_bar, std::span<uint64_t> a) const;

    /**
     * @brief Множення образів Монтгомері: res_bar = REDC(a_bar * b_bar)
     */
    void multiply(std::span<const uint64_t> a_bar,
                  std::span<const uint64_t> b_bar,
                  std::span<uint64_t> res_bar) const;

    /**
     * @brief Піднесення до квадрата у просторі Монтгомері
     */
    void square(std::span<const uint64_t> a_bar,
                std::span<uint64_t> res_bar) const;

    /**
     * @brief Сталочасове модулярне експоненціювання: res = base^exp mod N
     */
    void exponentiate(std::span<const uint64_t> base,
                      std::span<const uint64_t> exp,
                      std::span<uint64_t> res) const;

private:
    size_t k_;
    uint64_t n0_prime_;
    std::vector<uint64_t> n_;
    std::vector<uint64_t> r2_;
    mutable std::vector<uint64_t> workspace_;

    void compute_r2();
};

} // namespace bignum

#endif // MONTGOMERY_CONTEXT_HPP
