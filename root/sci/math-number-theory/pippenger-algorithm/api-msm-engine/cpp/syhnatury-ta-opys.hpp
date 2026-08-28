namespace msm {

/**
 * Розрахунок мінімального обсягу пам'яті арени для заданого розміру задачі.
 */
[[nodiscard]] size_t calculate_arena_size(const Config& config, size_t n) noexcept;

/**
 * Високорівневий інтерфейс обчислення MSM за алгоритмом Піппенджера.
 *
 * @param points  Вхідний масив афінних точок базису.
 * @param scalars Вхідний масив скалярів однакової розмірності.
 * @param config  Конфігураційні параметри рушія.
 * @return Результуюча точка або код помилки (std::expected).
 */
[[nodiscard]] std::expected<PointJacobian, Status> execute(
    std::span<const PointAffine> points,
    std::span<const FieldElement256> scalars,
    const Config& config = Config{}
);

/**
 * Пакетне перетворення точок з координат Якобі в афінні координати.
 */
[[nodiscard]] std::expected<std::vector<PointAffine>, Status> batch_to_affine(
    std::span<const PointJacobian> in_jacobian,
    CurveId curve = CurveId::BN254
);

} // namespace msm
