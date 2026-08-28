#include "main.h"   // CubeMX: ADC1, канали IN0/IN1/IN2 (PA0/PA1/PA2), 12 біт

extern ADC_HandleTypeDef hadc1;

static const float VREF = 3.3f;     // опора АЦП = живлення давача (ратіометрично)
static const float BIAS = 1.65f;    // 0g при 3.3 В ≈ половина живлення
static const float SENS = 0.330f;   // чутливість при 3.3 В ≈ 330 мВ/g

// Три осі йдуть на один АЦП по черзі: перемикаємо його мультиплексор
// і робимо одне перетворення.
static float read_axis_g(uint32_t channel)
{
    ADC_ChannelConfTypeDef ch = {
        .Channel      = channel,
        .Rank         = ADC_REGULAR_RANK_1,
        // вихід давача має 32 кОм усередині — беремо найдовшу вибірку,
        // щоб конденсатор АЦП устиг зарядитися (назва константи залежить від серії)
        .SamplingTime = ADC_SAMPLETIME_239CYCLES_5,
    };
    HAL_ADC_ConfigChannel(&hadc1, &ch);

    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    uint32_t raw = HAL_ADC_GetValue(&hadc1);   // 0..4095 (12 біт)
    HAL_ADC_Stop(&hadc1);

    float u = raw * VREF / 4095.0f;            // код → вольти
    return (u - BIAS) / SENS;                  // вольти → g
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_ADC1_Init();
    MX_USART2_UART_Init();      // printf перенаправлено на UART

    while (1) {
        printf("%.2f\t%.2f\t%.2f\r\n",
               read_axis_g(ADC_CHANNEL_0),
               read_axis_g(ADC_CHANNEL_1),
               read_axis_g(ADC_CHANNEL_2));
        HAL_Delay(50);
    }
}
