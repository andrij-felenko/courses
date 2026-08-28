namespace spatial {

class Morton2D {
public:
    static constexpr uint64_t encode(uint32_t x, uint32_t y) noexcept;
    static std::pair<uint32_t, uint32_t> decode(uint64_t z) noexcept;
};

class Morton3D {
public:
    static constexpr uint64_t encode(uint32_t x, uint32_t y, uint32_t z) noexcept;
    static std::tuple<uint32_t, uint32_t, uint32_t> decode(uint64_t key) noexcept;
};

class MortonIndex2D {
public:
    explicit MortonIndex2D(std::vector<Point2D> points);

    [[nodiscard]] std::vector<Point2D> query_range(const BoundingBox2D& box) const;
    [[nodiscard]] size_t size() const noexcept;
};

} // namespace spatial
