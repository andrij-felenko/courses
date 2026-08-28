#include <cmath>

struct Vec2 { float x, y; };

// Поворот вектора v на кут theta (радіани) проти годинникової стрілки.
Vec2 rotate2(Vec2 v, float theta) {
    const float c = std::cos(theta);
    const float s = std::sin(theta);
    return {
        v.x * c - v.y * s,   // перший рядок матриці
        v.x * s + v.y * c,   // другий рядок матриці
    };
}
