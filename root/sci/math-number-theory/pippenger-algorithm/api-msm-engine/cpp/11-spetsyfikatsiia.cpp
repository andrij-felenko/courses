namespace msm {

/**
 * Пакетне виконання K мультискалярних множень над спільним базисом.
 */
[[nodiscard]] std::expected<std::vector<PointJacobian>, Status> execute_batched(
    std::span<const PointAffine> points,
    std::span<const std::vector<FieldElement256>> batch_scalars,
    const Config& config = Config{}
);

} // namespace msm
