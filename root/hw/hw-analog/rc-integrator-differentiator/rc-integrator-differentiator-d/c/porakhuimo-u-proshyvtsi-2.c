// Цифровий двійник RC-диференціатора: вихід ∝ швидкості зміни входу.
static float v_prev = 0.0f;

float rc_differentiate(float v_in) {
    const float dt  = 0.1e-3f;          // крок 0.1 мс
    const float tau = 5.0e-3f;          // та сама стала часу
    float deriv = tau * (v_in - v_prev) / dt;   // τ · dV/dt
    v_prev = v_in;
    return deriv;                       // сплеск на зміні, нуль на сталому вході
}
