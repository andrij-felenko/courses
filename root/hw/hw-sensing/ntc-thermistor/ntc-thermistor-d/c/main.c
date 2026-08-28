// 12-бітний АЦП (0..4095), опорний резистор зверху, NTC знизу
// Vcc скорочується, тож працюємо прямо з відліком raw
float ntc_temperature_c(int raw) {
    const float R_REF = 10000.0f;   // опорний резистор, Ом
    const float R25   = 10000.0f;   // опір NTC за 25 °C
    const float BETA  = 3950.0f;    // B-параметр, K
    const float T25   = 298.15f;    // 25 °C у кельвінах

    float ratio = raw / 4095.0f;            // частка від повної шкали = U_сер/Vcc
    float r_ntc = R_REF * ratio / (1.0f - ratio);   // опір NTC з дільника
    float invT  = 1.0f / T25 + logf(r_ntc / R25) / BETA;
    return 1.0f / invT - 273.15f;           // назад у °C
}
