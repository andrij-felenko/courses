namespace geo {
    struct Interval {
        double low;
        double high;

        [[nodiscard]] constexpr bool overlaps(const Interval& other) const noexcept;
        [[nodiscard]] constexpr bool contains(double point) const noexcept;
        [[nodiscard]] constexpr bool encloses(const Interval& other) const noexcept;
    };
}
