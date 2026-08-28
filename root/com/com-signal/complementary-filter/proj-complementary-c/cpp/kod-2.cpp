void comp_step(Comp *c, float gx, float gy,
               float ax, float ay, float az, float dt)
{
    /* 1. опорні кути з акселерометра (atan2f — стійкий у всіх чвертях) */
    float roll_acc  = atan2f(ay, az);
    float pitch_acc = atan2f(-ax, sqrtf(ay*ay + az*az));

    /* 2. засіяти стартову оцінку показом акселерометра, не нулем */
    if (!c->seeded) {
        c->roll  = roll_acc;
        c->pitch = pitch_acc;
        c->seeded = 1;
        return;                 /* перший такт лише сіє, не інтегрує */
    }

    /* 3. вимикач довіри: якщо |a| далеко від g — підняти alpha майже до 1 */
    float amag = sqrtf(ax*ax + ay*ay + az*az);
    float a = c->alpha;
    if (fabsf(amag - c->g) > c->acc_band)
        a = 0.999f;             /* маневр: майже самий гіроскоп */

    /* 4. зважена сума окремо по кожній осі, кожна — своя вісь гіроскопа */
    c->roll  = a * (c->roll  + gx * dt) + (1.0f - a) * roll_acc;
    c->pitch = a * (c->pitch + gy * dt) + (1.0f - a) * pitch_acc;
}
