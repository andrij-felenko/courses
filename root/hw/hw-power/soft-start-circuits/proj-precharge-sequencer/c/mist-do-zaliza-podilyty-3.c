// Ковзне середнє на 8 вибірок: гасить шум АЦП, O(1) на крок.
#define FILT_N 8u
static uint32_t f_buf[FILT_N];
static uint32_t f_sum;
static uint8_t  f_idx, f_fill;

static uint32_t filter_push(uint32_t x)
{
    f_sum -= f_buf[f_idx];      // прибрати найстаріше
    f_buf[f_idx] = x;           // покласти найновіше
    f_sum += x;
    f_idx = (uint8_t)((f_idx + 1u) % FILT_N);
    if (f_fill < FILT_N) f_fill++;
    return f_sum / (f_fill ? f_fill : 1u);
}
