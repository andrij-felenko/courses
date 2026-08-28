/* Трапецієвий (Тастін) інтегратор: O(dt^2), точна фаза.
   Один зайвий доданок проти прямокутника — а порядок точності вищий. */
static float integ = 0.0f;   /* накопичений інтеграл */
static float e_prev = 0.0f;  /* попередній вхід */
float integrate_tustin(float e, float dt)
{
    integ  += 0.5f * (e + e_prev) * dt;   /* площа трапеції за крок */
    e_prev  = e;
    return integ;
}
