// Монітор струму: шунт 5 мОм + підсилювач G=50 + 12-біт АЦП (STM32 HAL)
#include "main.h"

#define R_SHUNT 0.005f            // Ом
#define GAIN    50.0f             // коефіцієнт підсилювача струму
#define VREF    3.3f              // опорна напруга АЦП, В
#define ADC_MAX 4095              // 12 біт

extern ADC_HandleTypeDef hadc1;   // канал із виходом підсилювача, налаштований у CubeMX
static float  i_zero = 0.0f;      // калібрований нуль (привид від offset), А
static double charge_mAh = 0.0;   // накопичений заряд

// Перевести «сирий» код АЦП у струм через шунт (закон Ома, назад через тракт)
float read_current(void) {
    HAL_ADC_Start(&hadc1);
    if (HAL_ADC_PollForConversion(&hadc1, 10) != HAL_OK) { HAL_ADC_Stop(&hadc1); return 0.0f; }
    uint32_t raw = HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);
    float v_adc = (float)raw / ADC_MAX * VREF;    // напруга на вході АЦП, В
    float v_sh  = v_adc / GAIN;                   // спад на самому шунті, В
    return v_sh / R_SHUNT - i_zero;               // I = V/R, мінус нуль
}

// Калібрування нуля: викликати, коли точно відомо, що струму немає
void calibrate_zero(void) {
    float acc = 0.0f;
    for (int k = 0; k < 64; k++) { acc += read_current() + i_zero; HAL_Delay(2); }
    i_zero = acc / 64.0f;                         // усереднений привид від offset
}

// Інтегрувати заряд: Q += I·Δt  (coulomb counter)
void accumulate_charge(float dt_s) {
    charge_mAh += (double)read_current() * dt_s / 3.6;   // А·с → мА·год: ділимо на 3.6
}
