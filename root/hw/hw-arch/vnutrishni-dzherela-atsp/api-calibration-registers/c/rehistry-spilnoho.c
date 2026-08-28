#include <stdint.h>

/* Бітові маски та зміщення регістра ADC_CCR (STM32 ADC Common Control Register) */
#define ADC_CCR_VREFEN_Pos      (22U)
#define ADC_CCR_VREFEN_Msk      (0x1UL << ADC_CCR_VREFEN_Pos)
#define ADC_CCR_VREFEN          ADC_CCR_VREFEN_Msk      /* Дозвіл буфера VREFINT */

#define ADC_CCR_TSEN_Pos        (23U)
#define ADC_CCR_TSEN_Msk        (0x1UL << ADC_CCR_TSEN_Pos)
#define ADC_CCR_TSEN            ADC_CCR_TSEN_Msk        /* Дозвіл датчика температури */

#define ADC_CCR_VBATEN_Pos      (24U)
#define ADC_CCR_VBATEN_Msk      (0x1UL << ADC_CCR_VBATEN_Pos)
#define ADC_CCR_VBATEN          ADC_CCR_VBATEN_Msk      /* Дозвіл внутрішнього дільника VBAT */

#define ADC_CCR_PRESC_Pos       (18U)
#define ADC_CCR_PRESC_Msk       (0xFUL << ADC_CCR_PRESC_Pos) /* Дільник тактування АЦП */
