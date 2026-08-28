namespace msm {

class FixedBaseTable {
public:
    explicit FixedBaseTable(
        std::span<const PointAffine> points,
        uint32_t window_size = 4,
        CurveId curve = CurveId::BN254
    );
    ~FixedBaseTable();

    FixedBaseTable(const FixedBaseTable&) = delete;
    FixedBaseTable& operator=(const FixedBaseTable&) = delete;

    FixedBaseTable(FixedBaseTable&&) noexcept = default;
    FixedBaseTable& operator=(FixedBaseTable&&) noexcept = default;

    [[nodiscard]] std::expected<PointJacobian, Status> execute(
        std::span<const FieldElement256> scalars
    ) const noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace msm
