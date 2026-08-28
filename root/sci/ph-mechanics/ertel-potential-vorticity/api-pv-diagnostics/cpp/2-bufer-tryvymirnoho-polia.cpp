struct Field3DView {
    std::span<const double> data;
    size_t stride_x{0};
    size_t stride_y{0};
    size_t stride_z{0};

    [[nodiscard]] constexpr size_t index(size_t i, size_t j, size_t k) const noexcept {
        return i * stride_x + j * stride_y + k * stride_z;
    }

    [[nodiscard]] constexpr double operator()(size_t i, size_t j, size_t k) const noexcept {
        return data[index(i, j, k)];
    }
};
