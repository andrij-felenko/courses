#include "stm32l0xx.h"   // приклад для родини STM32L0; регістри аналогічні в інших

// Адреса заводського калібрування VREFINT (див. довідник конкретного чипа).
// Значення знято за Vdd = 3.300 В, T ≈ 30 °C.
#define VREFINT_CAL   (*(volatile uint16_t *)0x1FF80078U)
#define VREFINT_CAL_VDD_MV   3300U

// Прочитати живлення (Vdda) у мілівольтах через заводськи калібрований VREFINT.
uint16_t read_vdda_mv(uint16_t vrefint_raw) {
    if (vrefint_raw == 0) return 0;
    // Vdda = 3300 мВ × VREFINT_CAL / поточний_відлік
    return (uint16_t)((uint32_t)VREFINT_CAL_VDD_MV * VREFINT_CAL / vrefint_raw);
}
