namespace msm {

struct Telemetry {
    double total_time_ms{0.0};
    double bucket_accum_time_ms{0.0};
    double running_sum_time_ms{0.0};
    double horner_time_ms{0.0};
    uint64_t mixed_additions_cnt{0};
    uint64_t jacobian_doublings_cnt{0};
    double memory_bandwidth_gb_s{0.0};
};

struct ExecutionResult {
    PointJacobian point;
    Telemetry telemetry;
};

/**
 * Виконання MSM зі збором телеметрії.
 */
[[nodiscard]] std::expected<ExecutionResult, Status> execute_profiled(
    std::span<const PointAffine> points,
    std::span<const FieldElement256> scalars,
    const Config& config = Config{}
);

} // namespace msm
