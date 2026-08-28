#include "driver/i2c.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// ── Плата: під свій мікроконтролер ─────────────────────────────
#define IRQ_GPIO             GPIO_NUM_4   // будь-який GPIO з перериванням
#define I2C_PORT             I2C_NUM_0
#define AS3935_ADDR          0x03         // ЗВІРИТИ з DIP-перемикачем!

// ── Налаштування під місце ─────────────────────────────────────
#define AS3935_CAPACITANCE   96           // стартова ємність, пФ (кратна 8)

static const char *TAG = "as3935";
static volatile bool irq_triggered = false;  // прапорець із обробника переривання

// Готової бібліотеки нема — говоримо з чіпом його регістрами напряму.
static esp_err_t as3935_write(uint8_t reg, uint8_t val) {
    uint8_t buf[2] = { reg, val };
    return i2c_master_write_to_device(I2C_PORT, AS3935_ADDR, buf, 2, pdMS_TO_TICKS(100));
}
static esp_err_t as3935_read(uint8_t reg, uint8_t *val) {
    return i2c_master_write_read_device(I2C_PORT, AS3935_ADDR, &reg, 1,
                                        val, 1, pdMS_TO_TICKS(100));
}
