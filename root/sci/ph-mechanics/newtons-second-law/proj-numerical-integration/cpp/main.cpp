struct Vec2 {
    double x{}, y{};
    Vec2 operator+(Vec2 b) const { return {x + b.x, y + b.y}; }
    Vec2 operator*(double s) const { return {x * s, y * s}; }
};
using Accel = Vec2 (*)(Vec2 r, Vec2 v);    // прискорення від стану

// Один крок явного Ейлера: обидва оновлення зі СТАРИХ значень.
void euler(Vec2& r, Vec2& v, Accel accel, double dt) {
    Vec2 a = accel(r, v);
    r = r + v * dt;
    v = v + a * dt;
}

// Напівнеявний Ейлер: усього один переставлений рядок.
void semi_implicit(Vec2& r, Vec2& v, Accel accel, double dt) {
    Vec2 a = accel(r, v);
    v = v + a * dt;                         // спершу швидкість…
    r = r + v * dt;                         // …положення вже НОВОЮ швидкістю
}
