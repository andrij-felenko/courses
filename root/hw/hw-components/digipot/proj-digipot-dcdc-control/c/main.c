#include <stdint.h>
#include <stdbool.h>

// Конфігурація апаратного вузла DC-DC та диджипота
#define DCDC_VFB_MV          800      // Опорна напруга FB, мВ (0.8 В)
#define DCDC_R1_OHM          33000    // Верхній резистор дільника, Ом
#define DCDC_R2_OHM          10000    // Базовий нижній резистор, Ом
#define DCDC_RS_OHM          4700     // Обмежувальний послідовний резистор, Ом

#define DIGIPOT_RAB_OHM      10000    // Повний номінал диджипота, Ом
#define DIGIPOT_RW_OHM       100      // Опір замкненого ключа повзунка, Ом
#define DIGIPOT_MAX_STEPS    255      // 8-бітний потенціометр (0..255)

// Команди керування (типовий протокол SPI)
#define CMD_WRITE_WIPER_RAM  0x00     // Запис у леткий регістр повзунка
#define CMD_WRITE_EEPROM     0x20     // Запис поточного значення в EEPROM
#define CMD_READ_WIPER       0x08     // Зчитування стану повзунка

typedef enum {
    DIGIPOT_OK = 0,
    DIGIPOT_ERR_VOLTAGE_OUT_OF_RANGE,
    DIGIPOT_ERR_HARDWARE_FAULT,
    DIGIPOT_ERR_TIMEOUT
} digipot_status_t;

// Апаратна абстракція SPI
typedef void (*spi_cs_func_t)(bool level);
typedef bool (*spi_transfer_func_t)(const uint8_t *tx, uint8_t *rx, uint16_t len);

typedef struct {
    spi_cs_func_t       set_cs;
    spi_transfer_func_t spi_xfer;
    uint8_t             current_code;
    uint16_t            min_safe_mv;
    uint16_t            max_safe_mv;
} digipot_t;

// Розрахунок вихідної напруги за кодом кроку (у мілівольтах)
uint16_t digipot_calculate_voltage(uint8_t code) {
    uint32_t r_branch = DCDC_RS_OHM + DIGIPOT_RW_OHM + 
                        ((uint32_t)code * DIGIPOT_RAB_OHM) / DIGIPOT_MAX_STEPS;
    
    // Паралельне з'єднання R2 та r_branch
    uint32_t r_bottom = (DCDC_R2_OHM * r_branch) / (DCDC_R2_OHM + r_branch);
    
    // V_out = V_FB * (1 + R1 / R_bottom)
    uint32_t v_out = DCDC_VFB_MV + (DCDC_VFB_MV * DCDC_R1_OHM) / r_bottom;
    return (uint16_t)v_out;
}

// Ініціалізація структури драйвера
digipot_status_t digipot_init(digipot_t *dev, spi_cs_func_t cs_fn, spi_transfer_func_t xfer_fn) {
    if (!dev || !cs_fn || !xfer_fn) {
        return DIGIPOT_ERR_HARDWARE_FAULT;
    }
    
    dev->set_cs = cs_fn;
    dev->spi_xfer = xfer_fn;
    dev->set_cs(true); // Деактивація CS (Active-Low)
    
    // Визначаємо фізично доступні межі напруг
    dev->min_safe_mv = digipot_calculate_voltage(DIGIPOT_MAX_STEPS);
    dev->max_safe_mv = digipot_calculate_voltage(0);
    dev->current_code = 128; // За замовчуванням mid-scale
    
    return DIGIPOT_OK;
}

// Прямий запис байта команди в диджипот по SPI
static digipot_status_t digipot_send_cmd(digipot_t *dev, uint8_t cmd, uint8_t data) {
    uint8_t tx_buf[2] = { cmd, data };
    uint8_t rx_buf[2] = { 0, 0 };
    
    dev->set_cs(false);
    bool ok = dev->spi_xfer(tx_buf, rx_buf, 2);
    dev->set_cs(true);
    
    if (!ok) {
        return DIGIPOT_ERR_HARDWARE_FAULT;
    }
    return DIGIPOT_OK;
}

// Встановлення точного коду кроку
digipot_status_t digipot_set_wiper_code(digipot_t *dev, uint8_t code) {
    digipot_status_t res = digipot_send_cmd(dev, CMD_WRITE_WIPER_RAM, code);
    if (res == DIGIPOT_OK) {
        dev->current_code = code;
    }
    return res;
}

// Встановлення бажаної вихідної напруги в мілівольтах
digipot_status_t digipot_set_target_voltage(digipot_t *dev, uint16_t target_mv) {
    if (target_mv < dev->min_safe_mv || target_mv > dev->max_safe_mv) {
        return DIGIPOT_ERR_VOLTAGE_OUT_OF_RANGE;
    }
    
    // Двійковий пошук оптимального коду кроку
    uint8_t best_code = 0;
    int32_t min_diff = 0x7FFFFFFF;
    
    for (int code = 0; code <= DIGIPOT_MAX_STEPS; code++) {
        uint16_t v = digipot_calculate_voltage((uint8_t)code);
        int32_t diff = (int32_t)v - (int32_t)target_mv;
        if (diff < 0) diff = -diff;
        
        if (diff < min_diff) {
            min_diff = diff;
            best_code = (uint8_t)code;
        }
    }
    
    return digipot_set_wiper_code(dev, best_code);
}

// Фіксація поточного положення повзунка в енергонезалежну пам'ять (EEPROM)
digipot_status_t digipot_save_to_eeprom(digipot_t *dev) {
    return digipot_send_cmd(dev, CMD_WRITE_EEPROM, dev->current_code);
}
