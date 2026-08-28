// реальний час: щокадру, тісно, без алокацій (напівнеявний Ейлер)
#include <cmath>
struct Vec2 { float x, y; };

static inline void step(Vec2& r, Vec2& v, float beta, float dt) {
    float sp = std::sqrt(v.x*v.x + v.y*v.y);     // |v| — повна швидкість
    float ax = -beta*sp*v.x;                     // a = g − β·|v|·v
    float ay = -9.81f - beta*sp*v.y;
    v.x += ax*dt;   v.y += ay*dt;                // СПЕРШУ швидкість…
    r.x += v.x*dt;  r.y += v.y*dt;               // …ТОДІ рух новою v — стійкіше
}
