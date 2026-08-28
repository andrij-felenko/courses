namespace msm {

/**
 * Валідація результату MSM проти еталонного оракула.
 */
[[nodiscard]] bool verify_against_oracle(
    const PointJacobian& result,
    std::span<const PointAffine> points,
    std::span<const FieldElement256> scalars,
    CurveId curve = CurveId::BN254
) noexcept;

} // namespace msm
