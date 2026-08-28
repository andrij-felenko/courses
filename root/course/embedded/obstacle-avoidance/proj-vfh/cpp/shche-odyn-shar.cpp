// Ваги ціни напрямку (ціль важить найбільше — тягне до мети).
#define W_GOAL   5.0f
#define W_CURR   2.0f
#define W_PREV   2.0f

static float g_prev_dir = 0.0f;    // торішній вибраний напрям (живе між тактами)

// Ціна одного кандидата-напрямку: менша — краща.
static float dir_cost(float cand, float goal_angle, float curr_heading)
{
    float cg = fabsf(angle_diff(cand, goal_angle));
    float cc = fabsf(angle_diff(cand, curr_heading));
    float cp = fabsf(angle_diff(cand, g_prev_dir));
    return W_GOAL * cg + W_CURR * cc + W_PREV * cp;
}
