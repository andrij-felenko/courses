#include "board_diag.h"
#include <stdio.h>
#include "esp_log.h"
#include "esp_rom_gpio.h"
#include "esp_vfs_dev.h"
#include "driver/usb_serial_jtag.h"
#include "driver/gpio.h"

static const char *TAG = "BOARD_DIAG";

esp_err_t board_diag_init_usb_cdc(void)
{
    ESP_LOGI(TAG, "Ініціалізація драйвера нативного USB CDC/JTAG...");

    usb_serial_jtag_driver_config_t usb_config = {
        .tx_buffer_size = 256,
        .rx_buffer_size = 256,
    };

    esp_err_t ret = usb_serial_jtag_driver_install(&usb_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Неможливо встановити драйвер USB Serial JTAG: %s", esp_err_to_name(ret));
        return ret;
    }

    // Реєстрація USB Serial JTAG у VFS для stdin/stdout
    esp_vfs_usb_serial_jtag_use_driver();
    ESP_LOGI(TAG, "Консоль USB CDC/JTAG VFS успішно активована");
    return ESP_OK;
}

esp_err_t board_diag_read_strapping_pins(board_strap_status_t *out_status)
{
    if (out_status == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    ESP_LOGI(TAG, "Зчитування станів конфігураційних виводів (strapping pins)...");

    // Використання esp_rom_gpio_pad_select_gpio для первинного налаштування падів
    esp_rom_gpio_pad_select_gpio(STRAP_GPIO_BOOT);
    esp_rom_gpio_pad_select_gpio(STRAP_GPIO_JTAG_SEL);
    esp_rom_gpio_pad_select_gpio(STRAP_GPIO_VDD_SPI);
    esp_rom_gpio_pad_select_gpio(STRAP_GPIO_LOG_DIS);

    // Конфігурація режимів входу для зчитування станів
    gpio_config_t strap_conf = {
        .pin_bit_mask = STRAP_MASK_BOOT | STRAP_MASK_JTAG_SEL | STRAP_MASK_VDD_SPI | STRAP_MASK_LOG_DIS,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    esp_err_t ret = gpio_config(&strap_conf);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка конфігурації GPIO для strapping pins: %s", esp_err_to_name(ret));
        return ret;
    }

    // Опитування логічних рівнів виводів
    int level_boot = gpio_get_level(STRAP_GPIO_BOOT);
    int level_jtag = gpio_get_level(STRAP_GPIO_JTAG_SEL);
    int level_vdd  = gpio_get_level(STRAP_GPIO_VDD_SPI);
    int level_log  = gpio_get_level(STRAP_GPIO_LOG_DIS);

    out_status->boot_mode = (level_boot != 0);
    out_status->jtag_sel = (level_jtag != 0);
    out_status->vdd_spi_1v8 = (level_vdd != 0);
    out_status->log_disabled = (level_log != 0);

    out_status->raw_value = (uint8_t)((level_boot & 0x01) |
                                      ((level_jtag & 0x01) << 1) |
                                      ((level_vdd & 0x01)  << 2) |
                                      ((level_log & 0x01)  << 3));

    return ESP_OK;
}

esp_err_t board_diag_test_gpio_loopback(gpio_num_t out_pin, gpio_num_t in_pin)
{
    ESP_LOGI(TAG, "Тестування петльового зв'язку (Loopback) між GPIO%d -> GPIO%d...", out_pin, in_pin);

    esp_rom_gpio_pad_select_gpio(out_pin);
    esp_rom_gpio_pad_select_gpio(in_pin);

    gpio_config_t out_conf = {
        .pin_bit_mask = (1ULL << out_pin),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&out_conf);

    gpio_config_t in_conf = {
        .pin_bit_mask = (1ULL << in_pin),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&in_conf);

    // Перевірка низького сигналу LOW
    gpio_set_level(out_pin, 0);
    esp_rom_delay_us(10);
    if (gpio_get_level(in_pin) != 0) {
        ESP_LOGE(TAG, "Помилка тесту: очікувався рівень 0 на GPIO%d", in_pin);
        return ESP_FAIL;
    }

    // Перевірка високого сигналу HIGH
    gpio_set_level(out_pin, 1);
    esp_rom_delay_us(10);
    if (gpio_get_level(in_pin) != 1) {
        ESP_LOGE(TAG, "Помилка тесту: очікувався рівень 1 на GPIO%d", in_pin);
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "Тест GPIO Loopback успішно пройдено!");
    return ESP_OK;
}

void board_diag_print_report(const board_strap_status_t *status)
{
    if (status == NULL) return;

    printf("\n=== ЗВІТ ДІАГНОСТИКИ СТАНОВ STRAPPING PINS ESP32-S3 ===\n");
    printf("Сигнальне бітове значення (RAW): 0x%02X\n", status->raw_value);
    printf("1. GPIO0  [BOOT Mode]:    %s (%s)\n",
           status->boot_mode ? "HIGH (1)" : "LOW (0)",
           status->boot_mode ? "SPI Flash Boot" : "Joint Download Boot");
    printf("2. GPIO3  [JTAG Select]:  %s (%s)\n",
           status->jtag_sel ? "HIGH (1)" : "LOW (0)",
           status->jtag_sel ? "eFuse/Hardware Controller" : "Software Controller");
    printf("3. GPIO45 [VDD_SPI Volts]: %s (%s)\n",
           status->vdd_spi_1v8 ? "HIGH (1)" : "LOW (0)",
           status->vdd_spi_1v8 ? "1.8V Flash/PSRAM" : "3.3V Flash/PSRAM");
    printf("4. GPIO46 [ROM Log Print]: %s (%s)\n",
           status->log_disabled ? "HIGH (1)" : "LOW (0)",
           status->log_disabled ? "Log Muted" : "Log Enabled during boot");
    printf("========================================================\n\n");
}
