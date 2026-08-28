/* Похідна назад — єдина придатна в реальному часі (лише минуле).
   Викликати щокроку; e_prev — похибка з попереднього кроку. */
static float e_prev = 0.0f;
float deriv_backward(float e, float dt)
{
    float d = (e - e_prev) / dt;   /* O(dt): нахил хорди, зсунутий на пів кроку */
    e_prev = e;
    return d;
}

/* Центральна різниця — O(dt^2), але потребує сусіда СПРАВА (майбутнє).
   Придатна лише коли весь ряд e[] уже в пам'яті (постобробка). */
float deriv_central(const float *e, int n, float dt)
{
    return (e[n + 1] - e[n - 1]) / (2.0f * dt);
}
