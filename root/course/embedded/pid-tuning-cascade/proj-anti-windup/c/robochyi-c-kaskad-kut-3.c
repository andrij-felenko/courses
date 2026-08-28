// Два регулятори каскаду — по одному на вісь (тут для одного каналу, напр. крен)
static pid_t angle_pid;   // зовнішній: кут → бажана швидкість
static pid_t rate_pid;    // внутрішній: швидкість → вплив на мотори

// Один крок каскаду для одного каналу.
float cascade_step(float angle_target, float angle_meas,
                   float gyro_rate, float dt)
{
    // ── ЗОВНІШНІЙ контур: його вихід — бажана кутова швидкість ────────────
    //     freeze_i вже виставлено з МИНУЛОГО кроку (див. кінець функції):
    //     якщо внутрішній тоді був у стелі — цей крок зовнішнього не накопичує.
    //     Межі u_min/u_max самого angle_pid = ±RATE_MAX (задано в init),
    //     тож вихід приходить уже обмеженим фізичною межею швидкості.
    pid_out_t outer = pid_update_ex(&angle_pid, angle_target, angle_meas, dt);
    float rate_setpoint = outer.u;

    // ── ВНУТРІШНІЙ контур: відпрацьовує (уже обмежену) бажану швидкість ───
    pid_out_t inner = pid_update_ex(&rate_pid, rate_setpoint, gyro_rate, dt);

    // ── НАСИЧЕННЯ ЗНИЗУ ВГОРУ: занотувати для наступного кроку зовнішнього ──
    //     впреться внутрішній у стелю — зовнішній наступного разу не накопичить.
    angle_pid.freeze_i = inner.saturated;

    return inner.u;   // це і йде в мотор-мікс
}
