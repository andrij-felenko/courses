#include <stdint.h>
#include <stdbool.h>

/* Коди помилок діагностики */
typedef enum {
    BRINGUP_OK = 0,
    BRINGUP_ERR_BUS_FAULT_0xFF,      /* Обрив лінії, немає живлення, лінія в підтяжці */
    BRINGUP_ERR_BUS_FAULT_0x00,      /* Замикання на GND, зависла шина */
    BRINGUP_ERR_SPI_PHASE_SHIFT,     /* Зсув бітів: хибний CPOL/CPHA */
    BRINGUP_ERR_WRONG_CHIP_ID,       /* Чужий ID: невідома ревізія або підробка */
    BRINGUP_ERR_SCRATCHPAD_FAILED,   /* Помилка двостороннього запису/читання */
    BRINGUP_ERR_TIMEOUT              /* Відсутня відповідь після N спроб */
} bringup_status_t;

/* Інтерфейс апаратного драйвера шини (HAL) */
typedef struct {
    bool (*read_reg)(uint8_t reg_addr, uint8_t *data);
    bool (*write_reg)(uint8_t reg_addr, uint8_t data);
    void (*delay_ms)(uint32_t ms);
} bus_driver_t;

/* Конфігурація цільового пристрою */
typedef struct {
    uint8_t who_am_i_reg;
    uint8_t expected_id;
    uint8_t scratchpad_reg;
} chip_config_t;

/* Повний діагностичний звіт */
typedef struct {
    bringup_status_t status;
    uint8_t          received_id;
    uint8_t          scratchpad_readback;
    uint8_t          failed_pattern;
} diagnostic_report_t;

diagnostic_report_t validate_chip_connection(const bus_driver_t *bus, const chip_config_t *cfg) {
    diagnostic_report_t report = {0};
    uint8_t read_val = 0;
    
    // 1. Апаратна пауза t_POR для стабілізації внутрішньої схеми скидання (зазвичай 5..20 мс)
    bus->delay_ms(15);
    
    // 2. Зчитування WHO_AM_I з повторними спробами (Retry loop)
    bool read_success = false;
    for (int retry = 0; retry < 5; ++retry) {
        if (bus->read_reg(cfg->who_am_i_reg, &read_val)) {
            read_success = true;
            break;
        }
        bus->delay_ms(2);
    }
    
    if (!read_success) {
        report.status = BRINGUP_ERR_TIMEOUT;
        return report;
    }
    
    report.received_id = read_val;
    
    // 3. Аналіз аномальних електричних станів шини
    if (read_val == 0xFF) {
        report.status = BRINGUP_ERR_BUS_FAULT_0xFF;
        return report;
    }
    if (read_val == 0x00) {
        report.status = BRINGUP_ERR_BUS_FAULT_0x00;
        return report;
    }
    
    // 4. Перевірка фазового зсуву бітів SPI (CPOL/CPHA)
    uint8_t shifted_left  = (uint8_t)(cfg->expected_id << 1);
    uint8_t shifted_right = (uint8_t)(cfg->expected_id >> 1);
    if (read_val == shifted_left || read_val == shifted_right) {
        report.status = BRINGUP_ERR_SPI_PHASE_SHIFT;
        return report;
    }
    
    // 5. Звірка з еталонним ідентифікатором
    if (read_val != cfg->expected_id) {
        report.status = BRINGUP_ERR_WRONG_CHIP_ID;
        return report;
    }
    
    // 6. Тест Scratchpad: перевірка тракту запису та читання
    const uint8_t test_patterns[] = {0x55, 0xAA, 0x00, 0xFF};
    uint8_t original_scratchpad_val = 0;
    
    // Збереження початкового стану конфігураційного регістра
    bus->read_reg(cfg->scratchpad_reg, &original_scratchpad_val);
    
    for (size_t i = 0; i < sizeof(test_patterns); ++i) {
        uint8_t pattern = test_patterns[i];
        uint8_t readback = 0;
        
        bus->write_reg(cfg->scratchpad_reg, pattern);
        bus->read_reg(cfg->scratchpad_reg, &readback);
        
        if (readback != pattern) {
            report.status = BRINGUP_ERR_SCRATCHPAD_FAILED;
            report.failed_pattern = pattern;
            report.scratchpad_readback = readback;
            
            // Спроба відновити вихідний стан перед аварійним виходом
            bus->write_reg(cfg->scratchpad_reg, original_scratchpad_val);
            return report;
        }
    }
    
    // Відновлення робочої конфігурації
    bus->write_reg(cfg->scratchpad_reg, original_scratchpad_val);
    
    report.status = BRINGUP_OK;
    return report;
}
