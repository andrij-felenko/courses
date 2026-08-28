#include <math.h>

// EMA, стійка до нерівних інтервалів: α перераховують із фактичного dt і сталої часу τ.
// Один пропущений відлік → більший dt → більша α → правильно сильніше забування.
float ema_dt(float x, float dt, float tau) {
    static float y = 0;
    static int primed = 0;
    if (!primed) { y = x; primed = 1; return y; }
    float alpha = 1.0f - expf(-dt / tau);   // α залежить від фактичного кроку часу
    y += alpha * (x - y);
    return y;
}
