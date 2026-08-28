namespace msm {

struct GlvDecomposedScalars {
    std::vector<FieldElement256> k1;
    std::vector<FieldElement256> k2;
};

/**
 * GLV-декомпозиція масиву скалярів.
 */
[[nodiscard]] std::expected<GlvDecomposedScalars, Status> glv_decompose_scalars(
    std::span<const FieldElement256> scalars,
    CurveId curve = CurveId::BN254
);

/**
 * Виконання комбінованого GLV-MSM.
 */
[[nodiscard]] std::expected<PointJacobian, Status> glv_execute(
    std::span<const PointAffine> points,
    std::span<const FieldElement256> k1,
    std::span<const FieldElement256> k2,
    const Config& config = Config{}
);

} // namespace msm
