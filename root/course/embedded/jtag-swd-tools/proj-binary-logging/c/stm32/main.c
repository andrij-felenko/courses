#include "stm32f4xx_hal.h"

extern UART_HandleTypeDef huart2;            // готує CubeMX: MX_USART2_UART_Init()
extern ADC_HandleTypeDef  hadc1;             // MX_ADC1_Init()

// ── Словник подій: ID замість рядків ──────────────────────────────────────
typedef enum {
    LOG_BOOT     = 0,   // "boot"
    LOG_TEMP     = 1,   // "temp=%d mV"
    LOG_VBAT_LOW = 2,   // "VBAT low %d"
} log_id_t;

// ── Кадр: [0x7E маркер][id][n байтів аргументів][XOR контроль] ────────────
static void blog(uint8_t id, const void *args, uint8_t n) {
    uint8_t f[4 + 8];
    uint8_t xor_sum = 0x7E ^ id ^ n;
    f[0] = 0x7E;                             // маркер-початок (ресинхронізація)
    f[1] = id;
    f[2] = n;
    for (uint8_t i = 0; i < n; i++) {
        f[3 + i] = ((const uint8_t *)args)[i];
        xor_sum ^= f[3 + i];
    }
    f[3 + n] = xor_sum;                      // контрольний байт (XOR усього кадру)
    HAL_UART_Transmit(&huart2, f, 4 + n, HAL_MAX_DELAY);
}

// ── Макрос: одна змінна, sizeof автоматично ───────────────────────────────
#define BLOG(id, val)  do { typeof(val) _v = (val); blog((id), &_v, sizeof(_v)); } while (0)

// один вимір АЦП у мілівольтах (опорна напруга 3300 мВ, 12 біт)
static uint16_t adc_mv(void) {
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    uint32_t raw = HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);
    return (uint16_t)(raw * 3300u / 4095u);
}

// ── Використання ──────────────────────────────────────────────────────────
int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART2_UART_Init();
    MX_ADC1_Init();
    blog(LOG_BOOT, NULL, 0);                 // подія без аргументів (n=0)

    while (1) {
        int16_t temp_mv = (int16_t)adc_mv();
        BLOG(LOG_TEMP, temp_mv);             // int16_t → 2 байти сирих у кадр
        // якщо напруга критична — сигналізуємо
        int16_t vbat_mv = (int16_t)adc_mv();
        if (vbat_mv < 3300) {
            BLOG(LOG_VBAT_LOW, vbat_mv);
        }
        HAL_Delay(100);
    }
}
