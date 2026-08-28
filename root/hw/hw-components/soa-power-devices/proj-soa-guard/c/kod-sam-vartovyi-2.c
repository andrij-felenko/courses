/* BUK7S1R0-40H: мережа Фостера, звірена з паспортним R_th(j-mb) = 0.4 К/Вт */
static const float FOSTER_R[SOA_STAGES] = {
    0.001935f, 0.002183f, 0.017918f, 0.123572f, 0.254393f      /* К/Вт */
};
static const float FOSTER_TAU[SOA_STAGES] = {
    0.2136e-6f, 6.658e-6f, 15.11e-6f, 847.4e-6f, 6.327e-3f     /* с */
};

#define DT_S     50e-6f     /* 20 кГц */
#define TJ_TRIP  150.0f     /* поріг: 25 К запасу під паспортні 175 °C */

static bool soa_curve_ok(float u, float i);   /* друга перевірка, нижче */

static soa_model      g_soa;
static volatile float g_tcase = 25.0f;   /* оновлює повільний цикл з NTC */

void soa_guard_init(void)
{
    soa_init(&g_soa, FOSTER_R, FOSTER_TAU, DT_S);
}

/* Переривання АЦП: U та I ВЗЯТІ ОДНОЧАСНО, здвоєним режимом */
void adc_isr(void)
{
    float u = uds_from_counts(ADC_DUAL->DR_A);    /* В */
    float i = id_from_counts(ADC_DUAL->DR_B);     /* А */
    float p = u * i;                              /* Вт — саме миттєвий добуток */

    float tj = g_tcase + soa_step(&g_soa, p);

    if (tj >= TJ_TRIP || !soa_curve_ok(u, i)) {
        fet_off();                    /* спершу залізо... */
        fault_latch(tj, u, i);        /* ...потім розбір польотів */
    }
}
