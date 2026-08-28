// Тривимірний вектор із константними операторами у C++20
struct DipoleVec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    constexpr DipoleVec3 operator+(const DipoleVec3& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    constexpr DipoleVec3 operator-(const DipoleVec3& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
    constexpr DipoleVec3 operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
};
