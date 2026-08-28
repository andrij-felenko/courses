#include "main.h"
extern ADC_HandleTypeDef hadc1;   // канал на нозі аналогового виходу 49E

#define DEADBAND 16               // мертва зона на 12-бітній шкалі

static uint16_t readAveraged(uint8_t n) {   // трохи усереднити проти шуму
    uint32_t acc = 0;
    for (uint8_t i = 0; i < n; i++) {
        HAL_ADC_Start(&hadc1);
        HAL_ADC_PollForConversion(&hadc1, 10);
        acc += HAL_ADC_GetValue(&hadc1);
        HAL_ADC_Stop(&hadc1);
    }
    return (uint16_t)(acc / n);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();               // D_Pin — звичайний вхід
    MX_ADC1_Init();

    HAL_Delay(50);                       // хай живлення й вихід 49E устояться
    int baseline = readAveraged(64);     // біля давача НЕ має бути магніту!
    printf("baseline = %d\r\n", baseline);

    while (1) {
        int delta = (int)readAveraged(8) - baseline;
        const char *pole = delta >  DEADBAND ? "N-бік"
                         : delta < -DEADBAND ? "S-бік" : "нема";
        // цифровий вихід D0 зазвичай активний у нулі
        int over = (HAL_GPIO_ReadPin(D_GPIO_Port, D_Pin) == GPIO_PIN_RESET);
        printf("поле: %d  (%s)%s\r\n", delta, pole, over ? "   [поріг!]" : "");
        HAL_Delay(100);
    }
}
