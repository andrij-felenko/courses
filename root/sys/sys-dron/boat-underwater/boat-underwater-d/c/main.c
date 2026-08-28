// Диференціальна (skid-steer) тяга для човна з двома рушіями.
// throttle, steering ∈ [-1, +1]; вихід — [-1, +1] на кожен рушій.
typedef struct { float left, right; } thrust_t;

static float clampf(float v, float lo, float hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

thrust_t mix_differential(float throttle, float steering) {
    thrust_t t;
    t.left  = throttle + steering;   // поворот праворуч → лівий сильніший
    t.right = throttle - steering;

    // Насичення: якщо сума вилізла за межу, стягуємо обидва порівну,
    // щоб зберегти намір повороту, а не «з'їсти» його обрізанням.
    float peak = fmaxf(fabsf(t.left), fabsf(t.right));
    if (peak > 1.0f) {
        t.left  /= peak;
        t.right /= peak;
    }
    t.left  = clampf(t.left,  -1.0f, 1.0f);
    t.right = clampf(t.right, -1.0f, 1.0f);
    return t;
}
