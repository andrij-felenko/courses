// ── М'який старт: плавно підняти шпаруватість від безпечного низу ──────────
#define SOFT_TARGET  (DUTY_MIN + 40u)   // куди дійти, перш ніж пускати P&O
#define SOFT_STEP     2u                // приріст за 1 мс

static bool soft_done = false;

static void soft_start_tick(void) {
    if (duty + SOFT_STEP >= SOFT_TARGET) { duty = SOFT_TARGET; soft_done = true; }
    else                                   duty += SOFT_STEP;
    pwm_set_duty(clamp_duty(duty));
}
