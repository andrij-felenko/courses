namespace thermo::api {
    [[nodiscard]] std::expected<ProcessRecord, Status> 
    solve_isochoric(const GasProperties& gas, const State& start, double target_t, double n_moles) noexcept;

    [[nodiscard]] std::expected<ProcessRecord, Status> 
    solve_isobaric(const GasProperties& gas, const State& start, double target_v, double n_moles) noexcept;

    [[nodiscard]] std::expected<ProcessRecord, Status> 
    solve_isothermal(const GasProperties& gas, const State& start, double target_v, double n_moles) noexcept;

    [[nodiscard]] std::expected<ProcessRecord, Status> 
    solve_adiabatic(const GasProperties& gas, const State& start, double target_v, double n_moles) noexcept;
}
