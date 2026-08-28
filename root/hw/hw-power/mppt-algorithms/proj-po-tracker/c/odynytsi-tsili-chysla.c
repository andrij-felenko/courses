#include <stdint.h>
#include <stdbool.h>

// Зовнішні залежності від драйверів конкретного МК:
extern uint16_t adc_read_raw(uint8_t ch);   // один сирий відлік 0..ADC_MAX
extern void     pwm_set_duty(uint16_t duty); // шпаруватість в одиницях таймера

#define ADC_MAX     4095u   // 12-бітний АЦП
#define CH_PANEL_V  0u
#define CH_PANEL_I  1u
#define CH_BATT_V   2u
#define CH_BATT_I   3u

// Калібрування «відлік → величина» лінійне: величина = відлік·(NUM/DEN).
// Дріб тримаємо цілим. Числа — приклад під конкретний дільник напруги й
// підсилювач шунта; на своїй платі їх заміряти й підставити.
#define PANEL_V_NUM 26000u   // повна шкала ≈ 26 В
#define PANEL_V_DEN  4095u
#define PANEL_I_NUM  8000u   // повна шкала ≈ 8 А
#define PANEL_I_DEN  4095u
