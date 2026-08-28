namespace math::number_theory {

// Обчислення двовимірної суми Якобі
[[nodiscard]] JacobiResult compute_jacobi(const PrimeField& field, uint64_t a, uint64_t b) noexcept;

// Обчислення багатовимірної суми Якобі J(χ_1, ..., χ_m)
[[nodiscard]] JacobiResult compute_jacobi(const PrimeField& field, std::span<const uint64_t> indices) noexcept;

// Точний підрахунок кількості розв'язків діофантового рівняння x^n + y^n = 1 mod p
[[nodiscard]] std::expected<int64_t, CurveError> count_fermat_points(const PrimeField& field, uint64_t n) noexcept;

} // namespace math::number_theory
