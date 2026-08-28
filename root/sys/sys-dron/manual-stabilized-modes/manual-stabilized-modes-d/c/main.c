// один такт внутрішньої петлі кутової швидкості (напр. на 400 Гц, dt = 0.0025 с)
float rate_pid_update(float target_dps, float gyro_dps, float dt,
                      PidState *s)
{
    float error = target_dps - gyro_dps;      // наскільки не так крутимось
    s->integ  += error * dt;                  // накопичена помилка
    float deriv = (error - s->prev_err) / dt; // як швидко міняється
    s->prev_err = error;

    return s->kp * error            // тягне до цілі зараз
         + s->ki * s->integ         // прибирає сталий недолік
         + s->kd * deriv;           // гасить розгойдування
}
