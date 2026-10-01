#ifndef BOARD_DIAG_H
#define BOARD_DIAG_H

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "driver/gpio.h"

// Конфігураційні виводи завантаження (Strapping Pins) ESP32-S3
#define STRAP_GPIO_BOOT        GPIO_NUM_0
#define STRAP_GPIO_JTAG_SEL    GPIO_NUM_3
#define STRAP_GPIO_VDD_SPI     GPIO_NUM_45
#define STRAP_GPIO_LOG_DIS     GPIO_NUM_46

// Бітові маски для зчитування strapping pins
#define STRAP_MASK_BOOT        (1ULL << STRAP_GPIO_BOOT)
#define STRAP_MASK_JTAG_SEL    (1ULL << STRAP_GPIO_JTAG_SEL)
#define STRAP_MASK_VDD_SPI     (1ULL << STRAP_GPIO_VDD_SPI)
#define STRAP_MASK_LOG_DIS     (1ULL << STRAP_GPIO_LOG_DIS)

// Тестові виводи периферії для перевірки сигналів
#define DIAG_TEST_GPIO_OUT     GPIO_NUM_17
#define DIAG_TEST_GPIO_IN      GPIO_NUM_18

// Структура результатів діагностики strapping pins
typedef struct {
    bool boot_mode;       // GPIO0: true = SPI Boot, false = Download Mode
    bool jtag_sel;        // GPIO3: true = Default JTAG, false = SW JTAG
    bool vdd_spi_1v8;     // GPIO45: true = 1.8V, false = 3.3V
    bool log_disabled;    // GPIO46: true = Log Disabled, false = Log Enabled
    uint8_t raw_value;    // Загальне 4-бітове значення
} board_strap_status_t;

// Прототипи функцій діагностики
esp_err_t board_diag_init_usb_cdc(void);
esp_err_t board_diag_read_strapping_pins(board_strap_status_t *out_status);
esp_err_t board_diag_test_gpio_loopback(gpio_num_t out_pin, gpio_num_t in_pin);
void board_diag_print_report(const board_strap_status_t *status);

#endif // BOARD_DIAG_H
