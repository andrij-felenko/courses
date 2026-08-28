// Пошук у відсортованому векторі Morton-точок у C++ (std::span)
std::vector<Point2D> morton_range_query2d(
    std::span<const Point2D> points,
    const BoundingBox2D& box
);

// Обчислення BIGMIN та LITMAX у C++ (std::pair)
std::pair<std::uint64_t, std::uint64_t> morton_bigmin_litmax2d(
    std::uint64_t curr_z,
    const BoundingBox2D& box
) noexcept;
