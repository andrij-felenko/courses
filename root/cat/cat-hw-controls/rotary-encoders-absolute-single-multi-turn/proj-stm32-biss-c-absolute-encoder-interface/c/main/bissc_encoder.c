#include "bissc_encoder.h"
#include <string.h>
#include "esp_log.h"
#include "esp_rom_sys.h"

static const char *TAG = "BISSC_DRIVER";

static bissc_config_t s_config;
static spi_device_handle_t s_spi_handle = NULL;

uint32_t bissc_gray_to_binary(uint32_t gray)
{
    uint32_t mask = gray >> 1;
    while (mask != 0) {
        gray ^= mask;
        mask >>= 1;
    }
    return gray;
}

uint8_t bissc_calculate_crc6(uint64_t data_val, uint8_t num_bits)
{
    // Генераторний поліном BiSS-C: P(x) = x^6 + x^1 + x^0 (0x43)
    // Обчислення виконується побітово від старшого до молодшого біта
    uint8_t crc = 0x00;
    for (int i = num_bits - 1; i >= 0; i--) {
        uint8_t bit = (data_val >> i) & 0x01;
        uint8_t crc_msb = (crc >> 5) & 0x01;
        crc = (crc << 1) & 0x3F;
        if (crc_msb ^ bit) {
            crc ^= 0x03; // Залишок від полінома 0x43 після зсуву (0x43 & 0x3F = 0x03)
        }
    }
    // Специфікація BiSS-C вимагає інверсії підсумкового значення CRC
    return crc ^ 0x3F;
}

esp_err_t bissc_encoder_init(const bissc_config_t *config)
{
    if (config == NULL || config->data_bits == 0 || config->data_bits > 32) {
        ESP_LOGE(TAG, "Некоректні параметри конфігурації BiSS-C енкодера");
        return ESP_ERR_INVALID_ARG;
    }

    memcpy(&s_config, config, sizeof(bissc_config_t));

    // Налаштування периферії SPI для тактування MA та зчитування SLO
    spi_bus_config_t buscfg = {
        .miso_io_num = config->pin_slo,
        .mosi_io_num = -1, // Двонаправлена шина не використовується для прийому
        .sclk_io_num = config->pin_ma,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 64
    };

    esp_err_t err = spi_bus_initialize(config->spi_host, &buscfg, SPI_DMA_CH_AUTO);
    if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
        ESP_LOGE(TAG, "Помилка ініціалізації шини SPI: %s", esp_err_to_name(err));
        return err;
    }

    // BiSS-C працює в режимі SPI Mode 2 (CPOL=1, CPHA=0) або Mode 3
    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = config->clock_speed_hz > 0 ? config->clock_speed_hz : 2000000,
        .mode = 2,
        .spics_io_num = -1, // CS не використовується, тактування безперервне
        .queue_size = 1,
    };

    err = spi_bus_add_device(config->spi_host, &devcfg, &s_spi_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка додавання пристрою SPI: %s", esp_err_to_name(err));
        return err;
    }

    ESP_LOGI(TAG, "Драйвер BiSS-C ініціалізовано (%d бітів позиції, %ld Гц)",
             config->data_bits, (long)config->clock_speed_hz);
    return ESP_OK;
}

esp_err_t bissc_encoder_read_frame(bissc_frame_t *out_frame)
{
    if (out_frame == NULL || s_spi_handle == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    memset(out_frame, 0, sizeof(bissc_frame_t));

    // Загальна довжина кадру: Позиція (N бітів) + Error (1 біт) + Warning (1 біт) + CRC (6 бітів)
    uint8_t total_payload_bits = s_config.data_bits + 2 + 6;
    uint8_t bytes_to_transfer = (total_payload_bits + 7) / 8 + 1; // Запас на вирівнювання

    uint8_t rx_buffer[8] = {0};

    spi_transaction_t t = {
        .length = bytes_to_transfer * 8,
        .rx_buffer = rx_buffer,
    };

    esp_err_t err = spi_device_polling_transmit(s_spi_handle, &t);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка передачі по SPI: %s", esp_err_to_name(err));
        return err;
    }

    // Упаковка байтів з буфера в 64-бітне слово для зручного виділення бітів
    uint64_t raw_stream = 0;
    for (int i = 0; i < bytes_to_transfer; i++) {
        raw_stream = (raw_stream << 8) | rx_buffer[i];
    }

    // Витягування складових кадру з урахуванням зсуву
    // Формат кадру BiSS-C: [POSITION (N bits)] [ERROR (1 bit)] [WARNING (1 bit)] [CRC (6 bits)]
    uint8_t crc_bits = 6;
    uint8_t crc_val = (uint8_t)(raw_stream & 0x3F); // Нижні 6 бітів — CRC
    uint8_t warning_bit = (uint8_t)((raw_stream >> 6) & 0x01);
    uint8_t error_bit = (uint8_t)((raw_stream >> 7) & 0x01);

    uint64_t pos_mask = (1ULL << s_config.data_bits) - 1;
    uint32_t raw_pos = (uint32_t)((raw_stream >> 8) & pos_mask);

    // У BiSS-C біти E та W є активними низькими (0 означає наявність апаратної помилки)
    out_frame->error_flag = (error_bit == 0);
    out_frame->warning_flag = (warning_bit == 0);
    out_frame->raw_position = raw_pos;
    out_frame->crc_received = crc_val;

    // Підготовка даних для обчислення CRC-6 (Позиція + E + W)
    uint64_t crc_data_input = ((uint64_t)raw_pos << 2) | ((error_bit & 1) << 1) | (warning_bit & 1);
    out_frame->crc_calculated = bissc_calculate_crc6(crc_data_input, s_config.data_bits + 2);
    out_frame->crc_valid = (out_frame->crc_received == out_frame->crc_calculated);

    // Декодування позиції (Код Ґрея у двійковий формат за потреби)
    if (s_config.is_gray_code) {
        out_frame->position = bissc_gray_to_binary(raw_pos);
    } else {
        out_frame->position = raw_pos;
    }

    // Перерахунок кутової координати у градуси
    double max_counts = (double)(1ULL << s_config.data_bits);
    out_frame->angle_degrees = (float)(((double)out_frame->position / max_counts) * 360.0);

    return ESP_OK;
}
