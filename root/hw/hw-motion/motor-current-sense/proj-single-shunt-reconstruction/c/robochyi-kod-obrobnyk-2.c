// Обробник «АЦП завершив обидва перетворення»: два коди → три фазні струми.
#define R_SHUNT   0.005f     // Ом
#define GAIN      20.0f      // підсилювач струму
#define VREF      3.3f
#define ADC_FS    4096.0f
static uint16_t g_zero = 2048;   // калібрований нуль (двонапрямлений вимір)

static inline float raw_to_current(uint16_t raw) {
    float v_out = ((int)raw - (int)g_zero) * (VREF / ADC_FS);
    return (v_out / GAIN) / R_SHUNT;      // I у шунті, зі знаком
}

volatile float g_ia, g_ib, g_ic;     // реконструйовані фазні струми, А
static  float  s_prev[3];            // струми минулого періоду (для сліпих зон)

void ADC1_2_IRQHandler(uint16_t raw1, uint16_t raw2) {
    recon_plan_t p = g_plan;           // знімок плану цього періоду

    // Струм у шунті в кожному вікні = ±струм конкретної фази (за таблицею вектора).
    float i_shunt1 = raw_to_current(raw1);
    float i_shunt2 = raw_to_current(raw2);

    // Розкладемо у масив фаз. Спершу — те, що зміряли напряму.
    float iph[3] = { 0.f, 0.f, 0.f };
    uint8_t known = 0;                 // бітова маска виміряних фаз

    iph[p.ph1] = p.sgn1 * i_shunt1;    // перша фаза: знак за таблицею
    known |= (1u << p.ph1);

    if (!p.blind) {
        iph[p.ph2] = p.sgn2 * i_shunt2;   // друга фаза з другого відліку
        known |= (1u << p.ph2);
    } else {
        // Сліпа зона: другу фазу беремо з минулого періоду (струм за 50 мкс майже не змінився).
        iph[p.ph2] = s_prev[p.ph2];
        known |= (1u << p.ph2);
    }

    // Третю (невиміряну) фазу добираємо з i_A + i_B + i_C = 0.
    uint8_t missing = 0;
    for (uint8_t k = 0; k < 3; k++)
        if (!(known & (1u << k))) missing = k;
    iph[missing] = -(iph[(missing + 1) % 3] + iph[(missing + 2) % 3]);

    g_ia = iph[0]; g_ib = iph[1]; g_ic = iph[2];
    s_prev[0] = g_ia; s_prev[1] = g_ib; s_prev[2] = g_ic;   // збережемо для наступних сліпих зон

    // далі: (g_ia,g_ib,g_ic) → перетворення Кларк/Парк → контур FOC
}
