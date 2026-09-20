#include "thumbwheel_74hc165.h"
#include <string.h>
#include "esp_log.h"
#include "esp_rom_sys.h"
#include "esp_timer.h"

static const char *TAG = "THUMBWHEEL_DRIVER";

static thumbwheel_config_t s_config;
static spi_device_handle_t s_spi_handle = NULL;
static thumbwheel_data_t s_last_stable_data = {0};
static int64_t s_last_valid_time = 0;

esp_err_t thumbwheel_init(const thumbwheel_config_t *config)
{
    if (config == NULL || config->num_digits == 0 || config->num_digits > THUMBWHEEL_MAX_DIGITS) {
        ESP_LOGE(TAG, "Некоректні параметри конфігурації BCD-перемикачів");
        return ESP_ERR_INVALID_ARG;
    }

    memcpy(&s_config, config, sizeof(thumbwheel_config_t));

    // Налаштування виводу PL (Parallel Load / Latch)
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << config->pin_pl),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    esp_err_t err = gpio_config(&io_conf);
    if (err != ESP_OK) {
        return err;
    }
    gpio_set_level(config->pin_pl, 1); // Нормальний стан PL — високий рівень

    // Конфігурація шини SPI для роботи з каскадом 74HC165
    spi_bus_config_t buscfg = {
        .miso_io_num = config->pin_miso,
        .mosi_io_num = -1, // Передача від МК не використовується
        .sclk_io_num = config->pin_sclk,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 32
    };

    err = spi_bus_initialize(config->spi_host, &buscfg, SPI_DMA_CH_AUTO);
    if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
        ESP_LOGE(TAG, "Помилка ініціалізації шини SPI: %s", esp_err_to_name(err));
        return err;
    }

    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = 1000000, // 1 МГц для надійної передачі
        .mode = 0,                 // SPI Mode 0 (CPOL=0, CPHA=0)
        .spics_io_num = -1,        // Chip Select не потрібен, використовуємо PL
        .queue_size = 1,
    };

    err = spi_bus_add_device(config->spi_host, &devcfg, &s_spi_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка додавання SPI пристрою 74HC165: %s", esp_err_to_name(err));
        return err;
    }

    ESP_LOGI(TAG, "Драйвер 74HC165 успішно ініціалізовано (%d декад BCD)", config->num_digits);
    return ESP_OK;
}

esp_err_t thumbwheel_read(thumbwheel_data_t *out_data)
{
    if (out_data == NULL || s_spi_handle == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    // 1. Формування короткачасового імпульсу защелкування PL (Parallel Load)
    // Активний низький імпульс (мінімум 20 нс за даташитом 74HC165)
    gpio_set_level(s_config.pin_pl, 0);
    esp_rom_delay_us(2);
    gpio_set_level(s_config.pin_pl, 1);
    esp_rom_delay_us(1);

    // 2. Зчитування байтів з каскаду 74HC165 через SPI
    // Кожен 74HC165 містить 8 бітів (дві 4-бітні BCD декади)
    uint8_t bytes_to_read = (s_config.num_digits + 1) / 2;
    uint8_t rx_buffer[4] = {0};

    spi_transaction_t t = {
        .length = bytes_to_read * 8,
        .rx_buffer = rx_buffer,
    };

    esp_err_t err = spi_device_polling_transmit(s_spi_handle, &t);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка SPI транзакції: %s", esp_err_to_name(err));
        return err;
    }

    // 3. Побітове декодування BCD-ніблів та перевірка транзитних станів
    thumbwheel_data_t current_data;
    memset(&current_data, 0, sizeof(thumbwheel_data_t));
    current_data.num_digits = s_config.num_digits;
    current_data.valid = true;

    uint32_t multiplier = 1;
    uint32_t total_val = 0;

    for (int i = 0; i < s_config.num_digits; i++) {
        uint8_t byte_idx = i / 2;
        uint8_t nibble_val;

        if (i % 2 == 0) {
            nibble_val = rx_buffer[byte_idx] & 0x0F;
        } else {
            nibble_val = (rx_buffer[byte_idx] >> 4) & 0x0F;
        }

        // Врахування інверсного підключення контактних груп
        if (s_config.active_low) {
            nibble_val = (~nibble_val) & 0x0F;
        }

        // Маскова перевірка невалідного BCD-значення (10..15):
        // (nibble & 0x08) != 0 та (nibble & 0x06) != 0 означає значення >= 10
        if (nibble_val > 9 || ((nibble_val & 0x08) && (nibble_val & 0x06))) {
            current_data.valid = false;
        }

        current_data.digits[i] = nibble_val;
        total_val += nibble_val * multiplier;
        multiplier *= 10;
    }

    current_data.raw_value = total_val;

    // 4. Програмна фільтрація брязкоту контактів (Debouncing)
    int64_t now = esp_timer_get_time() / 1000; // Час у мілісекундах

    if (!current_data.valid) {
        // Під час проміжного механічного перемикання повертаємо попередній стабільний кадр
        memcpy(out_data, &s_last_stable_data, sizeof(thumbwheel_data_t));
        out_data->valid = false;
        return ESP_OK;
    }

    if (memcmp(current_data.digits, s_last_stable_data.digits, s_config.num_digits) != 0) {
        // Якщо значення змінилося, очікуємо завершення інтервалу стабілізації
        if ((now - s_last_valid_time) >= s_config.debounce_ms) {
            memcpy(&s_last_stable_data, &current_data, sizeof(thumbwheel_data_t));
            s_last_valid_time = now;
        } else {
            current_data.valid = false;
        }
    } else {
        s_last_valid_time = now;
    }

    memcpy(out_data, &s_last_stable_data, sizeof(thumbwheel_data_t));
    out_data->valid = current_data.valid;
    return ESP_OK;
}
