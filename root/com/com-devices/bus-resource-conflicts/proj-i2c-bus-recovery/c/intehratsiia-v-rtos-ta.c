#include <stdint.h>
#include <stdbool.h>

// Типи FreeRTOS
typedef void* SemaphoreHandle_t;
extern SemaphoreHandle_t xSemaphoreCreateMutex(void);
extern bool xSemaphoreTake(SemaphoreHandle_t sem, uint32_t timeout_ms);
extern bool xSemaphoreGive(SemaphoreHandle_t sem);

extern i2c_recover_status_t i2c_bus_recover_9clocks(void);
extern bool hardware_i2c_transfer(uint8_t addr, const uint8_t* tx, uint16_t tx_len,
                                   uint8_t* rx, uint16_t rx_len, uint32_t timeout_ms);
extern void hardware_i2c_reinit(void);

static SemaphoreHandle_t s_i2c_mutex = NULL;

void i2c_bus_init(void)
{
    if (s_i2c_mutex == NULL) {
        s_i2c_mutex = xSemaphoreCreateMutex();
    }
    // Первинне відновлення шини перед увімкненням периферії
    i2c_bus_recover_9clocks();
    hardware_i2c_reinit();
}

bool i2c_safe_transfer(uint8_t addr, const uint8_t* tx, uint16_t tx_len,
                       uint8_t* rx, uint16_t rx_len, uint32_t timeout_ms)
{
    if (!xSemaphoreTake(s_i2c_mutex, timeout_ms)) {
        return false; // Тайм-аут очікування м'ютекса
    }

    bool success = hardware_i2c_transfer(addr, tx, tx_len, rx, rx_len, timeout_ms);

    if (!success) {
        // Транзакція провалилася (тайм-аут заліза або NACK)
        // Виконуємо відновлення 9 тактами та перезапуск периферії
        i2c_bus_recover_9clocks();
        hardware_i2c_reinit();

        // Повторна спроба після розблокування шини
        success = hardware_i2c_transfer(addr, tx, tx_len, rx, rx_len, timeout_ms);
    }

    xSemaphoreGive(s_i2c_mutex);
    return success;
}
