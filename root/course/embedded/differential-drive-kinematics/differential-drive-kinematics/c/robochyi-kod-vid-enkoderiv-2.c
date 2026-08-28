#define WHEEL_V_MAX_MPS  0.6f    // максимальна лінійна швидкість колеса, м/с

typedef struct { float left, right; } wheel_speeds_t;

wheel_speeds_t twist_to_wheels(float v, float w)
{
    wheel_speeds_t out;
    float half = 0.5f * w * TRACK_WIDTH_M;   // внесок повороту, ω·L/2

    out.right = v + half;   // обернена кінематика
    out.left  = v - half;

    // Насичення: жодне колесо не може бігти швидше за свою межу.
    // Масштабуємо ОБИДВІ швидкості разом, щоб не спотворити поворот.
    float m = fmaxf(fabsf(out.left), fabsf(out.right));
    if (m > WHEEL_V_MAX_MPS) {
        float k = WHEEL_V_MAX_MPS / m;
        out.left  *= k;
        out.right *= k;
    }
    return out;
}
