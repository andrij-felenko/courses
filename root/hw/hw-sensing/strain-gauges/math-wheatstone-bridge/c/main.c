// Повний міст, ratiometric АЦП: V_ref(АЦП) = V_зб(моста).
// Тоді V_зб скорочується, і код залежить лише від ΔR/R та підсилення.
#define GF        2.0f      // коефіцієнт тензочутливості
#define GAIN      128.0f    // підсилення інструментального підсилювача
#define ADC_FS    0x7FFFFF  // повна шкала 24-біт зі знаком (±)

// code = ADC_FS * GAIN * (V_вих / V_зб) = ADC_FS * GAIN * (ΔR/R)   [повний міст]
float strain_from_code(int32_t code)
{
    float ratio = (float)code / (float)ADC_FS;   // V_вих / V_зб, бо ref = збудження
    float dR_over_R = ratio / GAIN;              // знімаємо підсилення
    return dR_over_R / GF;                        // ε = (ΔR/R) / GF  → деформація
}
