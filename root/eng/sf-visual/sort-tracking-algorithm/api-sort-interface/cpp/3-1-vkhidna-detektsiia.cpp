struct Detection {
    float x1{0.0f};
    float y1{0.0f};
    float x2{0.0f};
    float y2{0.0f};
    float confidence{0.0f};
    int class_id{0};

    [[nodiscard]] constexpr float width() const noexcept { return x2 - x1; }
    [[nodiscard]] constexpr float height() const noexcept { return y2 - y1; }
    [[nodiscard]] constexpr float area() const noexcept { return width() * height(); }
};
