/* Стан регулятора — живе між викликами */
static float integral = 0.0f;   /* накопичена сума похибок (пам'ять I) */
static float e_prev   = 0.0f;   /* похибка з попереднього кроку (для D) */

/* Один крок PID. Викликати кожні dt секунд.
   setpoint — ціль, measured — показ датчика. Повертає керівний сигнал. */
float pid_step(float setpoint, float measured, float dt)
{
    float e = setpoint - measured;          /* поточна похибка */

    integral += e * dt;                     /* I: сума стовпчиків e·dt */
    float derivative = (e - e_prev) / dt;   /* D: різниця назад / dt */
    e_prev = e;                             /* запам'ятати для наступного кроку */

    return Kp * e
         + Ki * integral
         + Kd * derivative;                 /* P + I + D */
}
