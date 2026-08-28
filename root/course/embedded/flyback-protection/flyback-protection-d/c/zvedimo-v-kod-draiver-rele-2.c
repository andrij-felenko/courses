#include <stdint.h>

#define R_LIMIT_OHM     3300.0f   // обмежувальний резистор захисту входу, Ом
#define ADC_CIN_F       15e-12f   // ємність входу АЦП + доріжки, Ф

// Час установлення входу до 0.1% (≈7 сталих часу RC).
// Той самий резистор, що боронить від засувки, сповільнює вхід —
// тож вимірювати можна лише після цієї паузи.
static uint32_t adc_settle_us(void)
{
    float tau = R_LIMIT_OHM * ADC_CIN_F;     // τ = R·C
    return (uint32_t)(7.0f * tau * 1e6f) + 1;
}

uint16_t adc_read_protected(uint8_t channel)
{
    adc_select_channel(channel);
    delay_us(adc_settle_us());               // даємо RC-фільтру устоятися
    return adc_convert();
}
