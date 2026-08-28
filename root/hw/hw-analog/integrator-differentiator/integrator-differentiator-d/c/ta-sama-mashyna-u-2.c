// Диференціатор у прошивці = різниця сусідніх відліків / крок.
// Як і в залізі, чутливий до шуму, тож вхід варто згладити заздалегідь.
static float v_prev = 0.0f;
const float TAU = 0.02f;     // та сама стала R·C, що масштабує похідну

float differentiator_step(float v_in, float dt)
{
    float deriv = TAU * (v_in - v_prev) / dt;   // dV/dt чисельно
    v_prev = v_in;
    return deriv;
}
