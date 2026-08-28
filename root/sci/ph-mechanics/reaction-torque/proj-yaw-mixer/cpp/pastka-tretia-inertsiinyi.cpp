// Обмежувач наростання газу: гасить непотрібні J·α-ривки.
// max_step — максимальна зміна газу за один цикл керування.
void slew_limit(const float target[4], float state[4],
                float max_step, float out[4])
{
    for (int i = 0; i < 4; ++i) {
        float delta = target[i] - state[i];
        if (delta >  max_step) delta =  max_step;
        if (delta < -max_step) delta = -max_step;
        state[i] += delta;
        out[i]    = state[i];
    }
}
