// нормалізація з мертвою зоною навколо центру
float rc_normalize_dz(uint16_t pwm, uint16_t rc_min, uint16_t rc_trim,
                      uint16_t rc_max, uint16_t dz)
{
    // всередині мертвої зони — чистий нуль (гасимо тремтіння відпущеного стіка)
    if (pwm > rc_trim - dz && pwm < rc_trim + dz)
        return 0.0f;

    if (pwm >= rc_trim + dz)
        // права половина: відлік від краю мертвої зони, а не від trim
        return (float)(pwm - (rc_trim + dz)) / (rc_max - (rc_trim + dz));
    else
        // ліва половина: аналогічно від нижнього краю мертвої зони
        return (float)(pwm - (rc_trim - dz)) / ((rc_trim - dz) - rc_min);
}
