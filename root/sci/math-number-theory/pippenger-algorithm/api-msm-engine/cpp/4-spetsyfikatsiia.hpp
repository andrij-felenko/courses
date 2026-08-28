namespace msm {

enum class SerializationFormat : uint32_t {
    Uncompressed = 0,
    Compressed   = 1
};

/**
 * Серіалізація афінної точки у вектор байтів.
 */
[[nodiscard]] std::expected<std::vector<uint8_t>, Status> serialize_point(
    const PointAffine& point,
    SerializationFormat format = SerializationFormat::Compressed,
    CurveId curve = CurveId::BN254
);

/**
 * Десеріалізація точки з перевіркою рівняння кривої.
 */
[[nodiscard]] std::expected<PointAffine, Status> deserialize_point(
    std::span<const uint8_t> in_bytes,
    SerializationFormat format = SerializationFormat::Compressed,
    CurveId curve = CurveId::BN254
);

} // namespace msm
