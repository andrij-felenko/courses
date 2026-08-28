// Заводська калібрувальна константа STM32: сирий код VREFINT, знятий на заводі
// за VDDA = 3.0 В (значення й адреса — з даташита конкретного чіпа).
#define VREFINT_CAL   (*(volatile uint16_t*)0x1FFF7A2A)  // приклад для F4
#define VDDA_CAL_MV    3000u   // напруга, за якої знято VREFINT_CAL

// Читаємо ВЛАСНУ рейку, міряючи внутрішню опору проти рейки-як-опорної АЦП.
// Саме тому показ НЕ «пливе» разом із рейкою: точка відліку — стале band-gap,
// а не сама рейка. vref_raw — свіжий код каналу VREFINT (12-біт).
static uint16_t read_vdd_mv(uint16_t vref_raw) {
    if (vref_raw == 0) return 0;                 // захист від ділення на нуль
    // VDD = VDDA_cal × (код_заводський / код_поточний):
    return (uint16_t)(((uint32_t)VDDA_CAL_MV * VREFINT_CAL) / vref_raw);
}
