namespace uav::nav {

class ReturnBudgetEstimator {
public:
    explicit ReturnBudgetEstimator(const ReturnConfig& config);

    ReturnBudgetEstimator(const ReturnBudgetEstimator&) = delete;
    ReturnBudgetEstimator& operator=(const ReturnBudgetEstimator&) = delete;
    ReturnBudgetEstimator(ReturnBudgetEstimator&&) noexcept = default;
    ReturnBudgetEstimator& operator=(ReturnBudgetEstimator&&) noexcept = default;

    [[nodiscard]] std::optional<ReturnBudgetResult> update(
        const ReturnTelemetry& telemetry, 
        float dt_seconds
    );

    [[nodiscard]] float computeOptimalAirspeed(float headwind_component_ms) const noexcept;
    [[nodiscard]] float computeGroundSpeed(float airspeed_ms, float wind_speed_ms, float wind_angle_rad) const noexcept;
    [[nodiscard]] float estimateVoltageSag(float current_draw_a, float r_internal_ohms) const noexcept;

    void reset() noexcept;
};

} // namespace uav::nav
