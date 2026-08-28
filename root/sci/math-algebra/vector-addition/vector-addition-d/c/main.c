typedef struct { float x, y; } Vec2;

Vec2 vec2_add(Vec2 a, Vec2 b) {
    return (Vec2){ a.x + b.x, a.y + b.y };
}

/* використання */
Vec2 current  = {4.0f, 0.0f};   /* течія */
Vec2 paddling = {0.0f, 3.0f};   /* веслування */
Vec2 result   = vec2_add(current, paddling);

float speed = hypotf(result.x, result.y);     /* = 5.0 */
float angle = atan2f(result.y, result.x);     /* ≈ 0.6435 рад ≈ 36.87° */
