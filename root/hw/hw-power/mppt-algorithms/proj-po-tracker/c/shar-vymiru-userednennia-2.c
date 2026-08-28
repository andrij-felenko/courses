#define EMA_K  2u    // сила згладжування: більший k — тихіше, але повільніше

typedef struct {
    uint16_t vmv;    // напруга панелі, мВ
    uint16_t ima;    // струм панелі, мА
    int32_t  puw;    // потужність, мкВт
} meas_t;

static ema_t f_v, f_i;

static meas_t measure_panel(void) {
    meas_t m;
    m.vmv = ema_upd(&f_v, raw_to_mv(adc_avg(CH_PANEL_V)), EMA_K);
    m.ima = ema_upd(&f_i, raw_to_ma(adc_avg(CH_PANEL_I)), EMA_K);
    m.puw = (int32_t)m.vmv * (int32_t)m.ima;   // мВ×мА = мкВт, влазить у int32
    return m;
}
