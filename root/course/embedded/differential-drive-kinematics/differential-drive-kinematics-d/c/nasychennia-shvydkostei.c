#define WHEEL_V_MAX  0.6f    // стеля лінійної швидкості колеса, м/с

typedef struct { float left, right; } wheel_speeds_t;

typedef enum { KEEP_ARC, KEEP_TURN } sat_policy_t;

wheel_speeds_t twist_to_wheels_ex(float v, float w, sat_policy_t pol)
{
    float half = 0.5f * w * TRACK_WIDTH_M;   // внесок повороту, ω·L/2

    if (pol == KEEP_TURN) {
        // Поворот недоторканний: спершу вписуємо саму «половинку» повороту,
        // тоді доливаємо стільки v, скільки лишилось запасу.
        if (half >  WHEEL_V_MAX) half =  WHEEL_V_MAX;
        if (half < -WHEEL_V_MAX) half = -WHEEL_V_MAX;
        float v_room = WHEEL_V_MAX - fabsf(half);   // залишок під поступальний рух
        if (v >  v_room) v =  v_room;
        if (v < -v_room) v = -v_room;
    }

    wheel_speeds_t out;
    out.right = v + half;
    out.left  = v - half;

    if (pol == KEEP_ARC) {
        // Дуга недоторканна: жоден не за стелю, масштабуємо ПАРУ разом.
        float m = fmaxf(fabsf(out.left), fabsf(out.right));
        if (m > WHEEL_V_MAX) {
            float k = WHEEL_V_MAX / m;
            out.left  *= k;
            out.right *= k;
        }
    }
    return out;
}
