namespace acoustic {

[[nodiscard]] constexpr double calculate_total_spl(
    double spl_ref_db,
    double r_ref_m,
    double r_target_m,
    double alpha_db_m
) noexcept {
    if (r_target_m <= r_ref_m || r_ref_m <= 0.0) {
        return spl_ref_db;
    }
    const double div_loss = 20.0 * std::log10(r_target_m / r_ref_m);
    const double abs_loss = alpha_db_m * (r_target_m - r_ref_m);
    return spl_ref_db - div_loss - abs_loss;
}

} // namespace acoustic
