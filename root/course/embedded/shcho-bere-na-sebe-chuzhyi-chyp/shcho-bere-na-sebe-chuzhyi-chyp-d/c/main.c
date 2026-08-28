#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Регістри супутньої мікросхеми (Companion IC Registers) */
#define COMPANION_I2C_ADDR       (0x55 << 1)
#define REG_STATUS               0x00
#define REG_DATA_X               0x01
#define REG_DATA_Y               0x03
#define REG_BATTERY_SOC          0x05
#define REG_INT_CLEAR            0x0F

/* Бітові маски статусу */
#define STATUS_FLAG_TOUCH_EVT    (1 << 0)
#define STATUS_FLAG_LOW_BAT_EVT  (1 << 1)
#define STATUS_FLAG_CRYPTO_READY (1 << 2)

/* Структура телеметрії, вичитана з чипа */
typedef struct {
    uint16_t touch_x;
    uint16_t touch_y;
    uint8_t  battery_soc_pct;
    bool     crypto_ready;
} companion_telemetry_t;

/* Апаратні абстракції платформи (HAL stubs) */
extern bool hal_i2c_read_mem(uint16_t dev_addr, uint8_t reg_addr, uint8_t *buf, uint16_t len);
extern bool hal_i2c_write_reg(uint16_t dev_addr, uint8_t reg_addr, uint8_t val);

/* Глобальний прапорець асинхронної події з ISR */
static volatile bool s_companion_event_pending = false;

/**
 * @brief Обробник зовнішнього апаратного переривання від піна INT (Falling Edge)
 */
void companion_exti_isr(void) {
    /* Мінімальна робота в перериванні: фіксуємо подію */
    s_companion_event_pending = true;
}

/**
 * @brief Обробка подій супутнього чипа у фоновому циклі бізнес-логіки
 */
bool companion_process_events(companion_telemetry_t *out_data) {
    if (!s_companion_event_pending || out_data == NULL) {
        return false;
    }

    /* Атомарно скидаємо прапорець переривання для уникнення race condition */
    s_companion_event_pending = false;

    uint8_t status = 0;
    if (!hal_i2c_read_mem(COMPANION_I2C_ADDR, REG_STATUS, &status, 1)) {
        return false; /* Помилка зв'язку по шині */
    }

    /* Обробка події сенсорного вводу */
    if (status & STATUS_FLAG_TOUCH_EVT) {
        uint8_t raw_coords[4];
        if (hal_i2c_read_mem(COMPANION_I2C_ADDR, REG_DATA_X, raw_coords, 4)) {
            out_data->touch_x = (uint16_t)((raw_coords[0] << 8) | raw_coords[1]);
            out_data->touch_y = (uint16_t)((raw_coords[2] << 8) | raw_coords[3]);
        }
    }

    /* Обробка сповіщення про заряд батареї */
    if (status & STATUS_FLAG_LOW_BAT_EVT) {
        uint8_t soc = 0;
        if (hal_i2c_read_mem(COMPANION_I2C_ADDR, REG_BATTERY_SOC, &soc, 1)) {
            out_data->battery_soc_pct = soc;
        }
    }

    out_data->crypto_ready = (status & STATUS_FLAG_CRYPTO_READY) != 0;

    /* Квитування (квитування переривання в регістрах чипа для підняття лінії INT) */
    hal_i2c_write_reg(COMPANION_I2C_ADDR, REG_INT_CLEAR, 0x01);

    return true;
}
