#include "stm32f4xx_hal.h"

// Передискретизація з децимацією: 16 знімків → один 14-бітний результат.
// Сума ділиться на √16 = 4, а не на 16 — так зберігаються 2 додаткові біти.
//   ×4 знімків = +1 біт  →  ×16 = +2 біти  →  ділимо на 2² = 4.
// (На L4/G4/H7 те саме вміє саме залізо — поле Oversampling у налаштуванні АЦП:
//  Ratio = 16, RightBitShift = 2; тоді петля не потрібна взагалі.)
uint16_t oversample_14bit(ADC_HandleTypeDef *hadc) {
    uint32_t acc = 0;
    for (int i = 0; i < 16; i++) {
        HAL_ADC_Start(hadc);
        HAL_ADC_PollForConversion(hadc, 10);
        acc += HAL_ADC_GetValue(hadc);   // 12-бітні знімки (0..4095)
    }
    HAL_ADC_Stop(hadc);
    return (uint16_t)(acc >> 2);    // ÷4: результат уже 14-бітний (0..16380)
}
