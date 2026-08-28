namespace fdt {

class LinearResponseCalculator {
public:
    explicit LinearResponseCalculator(const PhysicalEnvironment& env) noexcept
        : env_(env) {}

    /// Обчислення причинної функції відгуку χ(t) за формулою Кубо
    [[nodiscard]] std::expected<std::vector<double>, FdtError>
    compute_response_function(std::span<const double> force,
                              std::span<const double> response,
                              double dt) const;

    /// Розрахунок квантового фактора Каллена-Велтона coth(ℏω / 2 k_B T)
    [[nodiscard]] double callen_welton_factor(double omega_rad_s) const noexcept;

    /// Розрахунок теоретичної спектральної густини флуктуацій за ТФД:
    /// S_A(ω) = ℏ · coth(ℏω / (2 k_B T)) · Im[χ(ω)]
    [[nodiscard]] std::expected<double, FdtError>
    theoretical_psd(double omega_rad_s, double im_chi) const noexcept;

private:
    PhysicalEnvironment env_;
};

class KramersKronigTransform {
public:
    /// Відновлення Re[χ(ω)] за відомим масивом Im[χ(ω)] через інтеграл головного значення Коші
    [[nodiscard]] static std::expected<std::vector<double>, FdtError>
    reconstruct_real_part(std::span<const double> omegas,
                          std::span<const double> im_chi);
};

} // namespace fdt
