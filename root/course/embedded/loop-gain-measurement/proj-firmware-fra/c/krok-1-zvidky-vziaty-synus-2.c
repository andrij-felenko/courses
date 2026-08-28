// CORDIC у Q15: повертає sin і cos кута angle (теж Q15-частка від π).
// Жодного множення в циклі — лише зсуви й додавання. Підходить ядрам без FPU.
static const int16_t cordic_atan[15] = {  // atan(2^-i), масштаб 2^15/π
    8192, 4836, 2555, 1297, 651, 326, 163, 81, 41, 20, 10, 5, 3, 1, 1
};
#define CORDIC_K  19898   // 0.607253 у Q15 — стале «стиснення» за всі ітерації

void cordic_sincos(int32_t angle, int16_t *s, int16_t *c) {
    int32_t x = CORDIC_K, y = 0, z = angle;
    for (int i = 0; i < 15; i++) {
        int32_t dx = x >> i, dy = y >> i;
        if (z >= 0) { x -= dy; y += dx; z -= cordic_atan[i]; }
        else        { x += dy; y -= dx; z += cordic_atan[i]; }
    }
    *c = (int16_t)x;   // cos
    *s = (int16_t)y;   // sin
}
