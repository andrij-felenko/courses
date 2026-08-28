#define PPS_OUTLIER_NS   500   /* стрибок більший — це збій, не дрейф */

static int32_t g_phase_prev_ns;

/* Відсіяти грубі викиди фази. true — зразок годиться для петлі. */
static bool pps_sane(int32_t phase_ns)
{
    int32_t jump = phase_ns - g_phase_prev_ns;
    if (jump < 0) jump = -jump;
    g_phase_prev_ns = phase_ns;
    return (jump < PPS_OUTLIER_NS);   /* різкий стрибок → відкинути */
}
