// Повний вихідний тракт: команди осей → газ кожного мотора → ESC.
// Викликається щоцикл керування (типово 1–8 кГц у сучасних FC).
void motor_output_stage(float throttle, float roll, float pitch, float yaw,
                        float slew_state[4], float max_step)
{
    float mixed[4], limited[4];

    // 1. Змішування з насиченням і пріоритетом осей.
    mix_saturate(throttle, roll, pitch, yaw, mixed);

    // 2. Обмеження наростання — гасимо зайві J·α-ривки.
    slew_limit(mixed, slew_state, max_step, limited);

    // 3. Віддати кожен газ своєму регулятору обертів.
    for (int i = 0; i < 4; ++i)
        esc_set_throttle(i, limited[i]);   // напр., через DShot
}
