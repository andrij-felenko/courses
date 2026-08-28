#pragma once

#include <span>
#include <cstddef>
#include <cstdint>
#include <expected>

namespace math::matrix {

class permanent_solver {
public:
    explicit permanent_solver(config cfg = {}) noexcept : cfg_(cfg) {}

    // Обчислення перманента для цілочисельного срізу std::span
    [[nodiscard]] std::expected<std::uint64_t, perm_errc>
    compute(std::span<const std::uint64_t> matrix, std::size_t n) const noexcept;

    // Обчислення перманента для дійсних чисел std::span
    [[nodiscard]] std::expected<double, perm_errc>
    compute(std::span<const double> matrix, std::size_t n) const noexcept;

    // Модульне обчислення перманента mod p
    [[nodiscard]] std::expected<std::uint64_t, perm_errc>
    compute_mod(std::span<const std::uint8_t> matrix, std::size_t n, std::uint64_t mod_p) const noexcept;

private:
    config cfg_;
};

} // namespace math::matrix
