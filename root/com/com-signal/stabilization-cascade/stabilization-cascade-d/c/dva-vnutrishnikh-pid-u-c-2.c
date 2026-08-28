// один такт каскаду стабілізації для ОДНІЄЇ осі (напр. крен).
// angle_sp     — бажаний кут (з пульта; для утримання горизонту = 0)
// angle_meas   — виміряний кут (з фільтра орієнтації)
// rate_meas    — виміряна кутова швидкість (НАПРЯМУ з гіроскопа)
float cascade_step(PID *outer, PID *inner,
                   float angle_sp, float angle_meas,
                   float rate_meas, float dt)
{
    // ЗОВНІШНІЙ контур (кут): його ВИХІД — це БАЖАНА кутова швидкість
    float rate_sp = pid_step(outer, angle_sp, angle_meas, dt);

    // ВНУТРІШНІЙ контур (швидкість): ціль — щойно отримана rate_sp
    float motor_cmd = pid_step(inner, rate_sp, rate_meas, dt);

    return motor_cmd;   // піде в мікшер моторів
}
