/* Спільні типи діагностичної прошивки та її публічний інтерфейс.
   Прошивка нічого не друкує: усі результати лягають у структуру звіту,
   яку відлагоджувач читає прямо з ОЗП. */
#ifndef BRINGUP_H
#define BRINGUP_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    BRINGUP_OK = 0,
    BRINGUP_ERR_HSE_TIMEOUT,      /* кварц не збудився */
    BRINGUP_ERR_PLL_TIMEOUT,      /* петля не захопила частоту */
    BRINGUP_ERR_I2C_TIMEOUT,      /* модуль не дійшов до наступного стану */
    BRINGUP_ERR_I2C_NACK,         /* адресу ніхто не підтвердив */
    BRINGUP_ERR_I2C_BUS_STUCK,    /* SDA лишилася притиснутою після 9 тактів */
    BRINGUP_ERR_ADC_TIMEOUT,      /* перетворення не завершилося */
    BRINGUP_ERR_VREF_UNCALIBRATED /* заводської константи в System ROM немає */
} bringup_status_t;

#define BRINGUP_I2C_MAX_FOUND 8

typedef struct {
    /* фаза 1 — тактові домени */
    bool hsi_ready;
    bool hse_ready;
    bool pll_ready;
    bringup_status_t clock_status;

    /* фаза 3 — шина I2C */
    bool i2c_bus_was_stuck;
    uint8_t i2c_devices_found;
    uint8_t i2c_addresses[BRINGUP_I2C_MAX_FOUND];
    bringup_status_t i2c_status;

    /* фаза 4 — опорне джерело й напруга живлення */
    uint16_t vrefint_raw;
    uint16_t vrefint_cal;
    uint32_t vdda_mv;
    bringup_status_t adc_status;
} bringup_report_t;

/* Ядро крутиться на HSI 16 МГц. Прошивка навмисно НЕ перемикається на PLL:
   вона перевіряє кварц, тож не має від нього залежати. Звідси й PCLK1. */
#define BRINGUP_CORE_HZ   16000000U
#define BRINGUP_PCLK1_HZ  16000000U
#define BRINGUP_HSE_HZ     8000000U

/* Груба затримка порожнім циклом: SysTick тут свідомо не заводимо, бо він
   теж частина того, що ми ще не перевірили. Точність нам і не потрібна —
   потрібні одиниці мікросекунд «не менше». Тіло циклу — приблизно 4 такти. */
#define BRINGUP_LOOPS_PER_US (BRINGUP_CORE_HZ / 4000000U)

static inline void bringup_delay_loops(uint32_t loops)
{
    volatile uint32_t n = loops;
    while (n > 0U) {
        --n;
    }
}

static inline void bringup_delay_us(uint32_t us)
{
    bringup_delay_loops(us * BRINGUP_LOOPS_PER_US);
}

/* фаза 1: HSI → HSE → PLL */
bringup_status_t bringup_clock_check(bringup_report_t *report);

/* фаза 2: меандр на контрольних майданчиках */
void bringup_gpio_toggle_testpoints(uint32_t iterations);

/* фаза 3: розблокування, ініціалізація та сканування шини */
bringup_status_t bringup_i2c_bus_clear(bool *was_stuck);
void bringup_i2c_init(void);
bringup_status_t bringup_i2c_probe_address(uint8_t addr_7bit);
bringup_status_t bringup_scan_i2c_bus(bringup_report_t *report);

/* фаза 4: VREFINT і реальна напруга VDDA */
bringup_status_t bringup_measure_vdda(bringup_report_t *report);

#endif /* BRINGUP_H */
