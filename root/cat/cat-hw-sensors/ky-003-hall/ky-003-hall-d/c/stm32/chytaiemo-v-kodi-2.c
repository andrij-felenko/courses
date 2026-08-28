#include "main.h"                  // A0 → PA0 (ADC1_IN0), D0 → D0_Pin із GPIO_PULLUP

extern ADC_HandleTypeDef hadc1;

static uint16_t sample(void) {
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    uint16_t v = HAL_ADC_GetValue(&hadc1);   // 0..4095
    HAL_ADC_Stop(&hadc1);
    return v;
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_ADC1_Init();

    long acc = 0;                  // за ~200 мс без магніту запамʼятовуємо реальний спокій
    for (int i = 0; i < 64; i++) { acc += sample(); HAL_Delay(3); }
    int baseline = (int)(acc / 64);   // ≈ половина шкали (живлення 3.3 В, 12 біт: ≈2048)

    while (1) {
        int delta = (int)sample() - baseline;   // >0 один полюс, <0 протилежний
        const char *pole = delta > 0 ? "(N-бік)" : (delta < 0 ? "(S-бік)" : "(нема)");
        printf("поле: %d %s%s\r\n", delta, pole,
               HAL_GPIO_ReadPin(D0_GPIO_Port, D0_Pin) == GPIO_PIN_RESET ? " [поріг!]" : "");
        HAL_Delay(100);
    }
}
