// ============================================================================
// C99 / STM32 LL (Low-Layer) & Direct Register Access
// ============================================================================
#include <stdint.h>
#include <stdbool.h>
#include "stm32l4xx.h"
#include "stm32l4xx_ll_bus.h"
#include "stm32l4xx_ll_gpio.h"
#include "stm32l4xx_ll_rcc.h"
#include "stm32l4xx_ll_adc.h"
#include "stm32l4xx_ll_i2c.h"
#include "stm32l4xx_ll_dma.h"
#include "stm32l4xx_ll_utils.h"

#define PIN_PHASE_SET()   (GPIOA->BSRR = GPIO_BSRR_BS0)
#define PIN_PHASE_CLR()   (GPIOA->BSRR = GPIO_BSRR_BR0)

#define PIN_SUB_SET()     (GPIOA->BSRR = GPIO_BSRR_BS1)
#define PIN_SUB_CLR()     (GPIOA->BSRR = GPIO_BSRR_BR1)

typedef struct {
    uint32_t pll_cycles;
    uint32_t vref_cycles;
    uint32_t adc_single_cycles;
    uint32_t i2c_poll_cycles;
    uint32_t i2c_dma_cycles;
    uint32_t crc_calc_cycles;
} benchmark_result_t;

static benchmark_result_t g_bench_res;

static void dwt_counter_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    DWT->CYCCNT = 0;
}

static inline uint32_t dwt_get_cycles(void) {
    return DWT->CYCCNT;
}

// ── 1. Вимірювання запуску та стабілізації PLL ──────────────────────────────
void bench_pll_startup(void) {
    PIN_PHASE_SET();
    uint32_t start = dwt_get_cycles();

    // Увімкнення фазового помножувача (PLL) від внутрішнього HSI (16 МГц) до 80 МГц
    LL_RCC_PLL_Enable();
    while (!LL_RCC_PLL_IsReady()) {
        // Очікування апаратного захоплення частоти (PLL Lock)
    }
    LL_RCC_SetSysClkSource(LL_RCC_SYS_CLKSOURCE_PLL);
    while (LL_RCC_GetSysClkSource() != LL_RCC_SYS_CLKSOURCE_STATUS_PLL) {
        // Очікування перемикання системного тактування
    }

    g_bench_res.pll_cycles = dwt_get_cycles() - start;
    PIN_PHASE_CLR();
}

// ── 2. Прогрів внутрішнього джерела VREF та оцифрування АЦП ──────────────────
uint16_t bench_adc_single_sample(void) {
    PIN_PHASE_SET();
    uint32_t start = dwt_get_cycles();

    // Увімкнення стабілізатора опорної напруги
    LL_ADC_EnableInternalRegulator(ADC1);
    // Апаратна затримка стабілізації VREF (типово 20 мкс)
    LL_mDelay(1); 

    LL_ADC_StartCalibration(ADC1, LL_ADC_SINGLE_ENDED);
    while (LL_ADC_IsCalibrationOnGoing(ADC1)) {}

    LL_ADC_Enable(ADC1);
    while (!LL_ADC_IsReady(ADC1)) {}

    PIN_SUB_SET();
    LL_ADC_REG_StartConversion(ADC1);
    while (!LL_ADC_IsActiveFlag_EOC(ADC1)) {}
    uint16_t raw_val = LL_ADC_REG_ReadConversionData12(ADC1);
    PIN_SUB_CLR();

    g_bench_res.adc_single_cycles = dwt_get_cycles() - start;
    PIN_PHASE_CLR();
    return raw_val;
}

// ── 3. Зчитування I2C давача: блокуючий полінг ───────────────────────────────
bool bench_i2c_read_polling(uint8_t dev_addr, uint8_t reg_addr, uint8_t *buf, uint16_t len) {
    PIN_PHASE_SET();
    uint32_t start = dwt_get_cycles();

    // Генерація START умови та передача адреси регістра
    LL_I2C_HandleTransfer(I2C1, dev_addr, LL_I2C_ADDRSLAVE_7BIT, 1, 
                          LL_I2C_MODE_SOFTEND, LL_I2C_GENERATE_START_WRITE);
    while (!LL_I2C_IsActiveFlag_TXIS(I2C1)) {}
    LL_I2C_TransmitData8(I2C1, reg_addr);
    while (!LL_I2C_IsActiveFlag_TC(I2C1)) {}

    // Повторний START на читання
    LL_I2C_HandleTransfer(I2C1, dev_addr, LL_I2C_ADDRSLAVE_7BIT, len, 
                          LL_I2C_MODE_AUTOEND, LL_I2C_GENERATE_START_READ);

    for (uint16_t i = 0; i < len; i++) {
        while (!LL_I2C_IsActiveFlag_RXNE(I2C1)) {
            // CPU активно молотить у циклі очікування байта шини
        }
        buf[i] = LL_I2C_ReceiveData8(I2C1);
    }
    while (!LL_I2C_IsActiveFlag_STOP(I2C1)) {}
    LL_I2C_ClearFlag_STOP(I2C1);

    g_bench_res.i2c_poll_cycles = dwt_get_cycles() - start;
    PIN_PHASE_CLR();
    return true;
}

// ── 4. Розрахунок поліноміальної контрольної суми CRC-16 ─────────────────────
uint16_t bench_calculate_crc16(const uint8_t *data, uint32_t length) {
    PIN_PHASE_SET();
    uint32_t start = dwt_get_cycles();

    uint16_t crc = 0xFFFF;
    for (uint32_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021; // Поліном CCITT
            } else {
                crc <<= 1;
            }
        }
    }

    g_bench_res.crc_calc_cycles = dwt_get_cycles() - start;
    PIN_PHASE_CLR();
    return crc;
}
