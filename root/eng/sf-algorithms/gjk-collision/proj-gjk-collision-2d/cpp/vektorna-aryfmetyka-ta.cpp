#include <cmath>
#include <array>
#include <span>
#include <iostream>
#include <optional>

struct Vec2 {
    float x{0.0f};
    float y{0.0f};

    constexpr Vec2() noexcept = default;
    constexpr Vec2(float x_, float y_) noexcept : x(x_), y(y_) {}

    constexpr Vec2 operator+(Vec2 rhs) const noexcept { return {x + rhs.x, y + rhs.y}; }
    constexpr Vec2 operator-(Vec2 rhs) const noexcept { return {x - rhs.x, y - rhs.y}; }
    constexpr Vec2 operator-() const noexcept { return {-x, -y}; }
    constexpr float dot(Vec2 rhs) const noexcept { return x * rhs.x + y * rhs.y; }
    constexpr float cross(Vec2 rhs) const noexcept { return x * rhs.y - y * rhs.x; }

    /* Потрійний векторний добуток: (this × b) × this */
    constexpr Vec2 triple_product(Vec2 b, Vec2 c) const noexcept {
        float z = x * b.y - y * b.x;
        return {-c.y * z, c.x * z};
    }
};

/* Опорна точка для опуклого многокутника */
inline Vec2 polygon_support(std::span<const Vec2> vertices, Vec2 dir) noexcept {
    if (vertices.empty()) return {};
    int best_index = 0;
    float max_dot = vertices[0].dot(dir);

    for (size_t i = 1; i < vertices.size(); ++i) {
        float dot = vertices[i].dot(dir);
        if (dot > max_dot) {
            max_dot = dot;
            best_index = static_cast<int>(i);
        }
    }
    return vertices[best_index];
}

/* Опорна точка для кола */
inline Vec2 circle_support(Vec2 center, float radius, Vec2 dir) noexcept {
    float len_sq = dir.dot(dir);
    if (len_sq < 1e-8f) return center;
    float inv_len = radius / std::sqrt(len_sq);
    return {center.x + dir.x * inv_len, center.y + dir.y * inv_len};
}
