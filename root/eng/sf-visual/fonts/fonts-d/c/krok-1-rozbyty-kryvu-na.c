// Точка на квадратичній кривій Безьє при параметрі t (0..1):
// P(t) = (1-t)^2·P0 + 2(1-t)t·P1 + t^2·P2,   P1 — керувальна
typedef struct { float x, y; } Pt;

Pt quad_bezier(Pt p0, Pt p1, Pt p2, float t) {
    float u = 1.0f - t;
    float a = u * u, b = 2.0f * u * t, c = t * t;
    Pt r = { a * p0.x + b * p1.x + c * p2.x,
             a * p0.y + b * p1.y + c * p2.y };
    return r;
}
// Криву обходять кроками t = 0, 1/n, 2/n, ... 1, з'єднуючи точки відрізками.
// n добирають за розміром: більший кегль → більше n.
