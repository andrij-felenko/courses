namespace msm {

/**
 * Емуляція виклику EVM Precompile G1 MSM.
 */
[[nodiscard]] std::expected<std::vector<uint8_t>, Status> evm_precompile_call(
    std::span<const uint8_t> calldata,
    CurveId curve = CurveId::BN254
);

} // namespace msm
