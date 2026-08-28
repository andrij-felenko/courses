/* --- Склеювання: один такт режиму Depth Hold --- */
static DepthSensor g_ds;
static DepthPID    g_pid;
static float       g_target_depth = 2.0f;   /* задана глибина, м         */

void depth_hold_setup(void)
{
    /* морська вода; α=0.25 — помірне згладжування; τ_d=0.08 c */
    depth_sensor_init(&g_ds, 1025.0f, 9.81f, 0.25f);
    /* kp,ki,kd підбирають під апарат; межі тяги −1..+1;
       інтеграл обмежуємо так, щоб він міг дати щонайбільше ~половину тяги */
    depth_pid_init(&g_pid, 4.0f, 1.2f, 2.5f, 0.08f,
                   -0.5f, 0.5f, -1.0f, 1.0f);
}

/* Викликати на поверхні перед зануренням. */
void depth_hold_arm(float p_abs_now)
{
    depth_sensor_tare(&g_ds, p_abs_now);
    depth_pid_reset(&g_pid, 0.0f);
}

/* Гарячий такт: dt — фактичний крок, с; read_pressure_pa() — ваш давач. */
float depth_hold_step(float dt)
{
    float p_abs = read_pressure_pa();                 /* сирий тиск, Па   */
    float depth = depth_from_pressure(&g_ds, p_abs);  /* → згладжена глибина */
    float u = depth_pid_step(&g_pid, g_target_depth, depth, dt);
    return u;   /* → на вертикальні рушії через мікшер */
}
