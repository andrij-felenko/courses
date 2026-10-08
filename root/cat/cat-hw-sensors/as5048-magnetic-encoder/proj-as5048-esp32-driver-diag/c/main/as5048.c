#include "as5048.h"
#include <stdlib.h>
#include <string.h>
#include "esp_log.h"

static const char *TAG = "AS5048";

/**
 * @brief Внутрішня структура контексту пристрою AS5048.
 */
struct as5048_dev_s {
    spi_device_handle_t spi_dev;
    gpio_num_t cs_io_num;
    uint16_t zero_offset;
};

uint16_t as5048_calculate_parity(uint16_t value)
{
    // Отримуємо 15 молодших бітів (біти 0..14)
    uint16_t v = value & 0x7FFF;
    v ^= v >> 8;
    v ^= v >> 4;
    v ^= v >> 2;
    v ^= v >> 1;
    // Якщо кількість 1-бітів непарна, повертаємо маску біта 15 для парної кількості (Even Parity)
    return (v & 1) ? AS5048_FRAME_PARITY_BIT : 0x0000;
}

/**
 * @brief Низькорівнева передача 16-бітного кадру по SPI та зчитування відповіді.
 */
static esp_err_t as5048_spi_transfer(as5048_handle_t handle, uint16_t tx_cmd, uint16_t *rx_val)
{
    if (!handle || !handle->spi_dev) {
        return ESP_ERR_INVALID_ARG;
    }

    // Формування кадру із розрахованим бітом парності
    uint16_t frame = tx_cmd & 0x7FFF;
    frame |= as5048_calculate_parity(frame);

    spi_transaction_t trans = {
        .flags = SPI_TRANS_USE_TXDATA | SPI_TRANS_USE_RXDATA,
        .length = 16,
        .tx_data = { (uint8_t)(frame >> 8), (uint8_t)(frame & 0xFF) }
    };

    esp_err_t ret = spi_device_transmit(handle->spi_dev, &trans);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка передачі SPI: %s", esp_err_to_name(ret));
        return ret;
    }

    uint16_t rx_raw = ((uint16_t)trans.rx_data[0] << 8) | trans.rx_data[1];

    // Перевірка цілісності отриманих даних (Even Parity)
    uint16_t expected_parity = as5048_calculate_parity(rx_raw & 0x7FFF);
    if ((rx_raw & AS5048_FRAME_PARITY_BIT) != expected_parity) {
        ESP_LOGE(TAG, "Збій перевірки парності SPI кадру: 0x%04X", rx_raw);
        return ESP_ERR_INVALID_CRC;
    }

    if (rx_val) {
        *rx_val = rx_raw;
    }

    return ESP_OK;
}

/**
 * @brief Допоміжна функція конвеєрного читання регістру AS5048.
 * AS5048 повертає результат попередньої команди, тому для отримання даних надсилається NOP.
 */
static esp_err_t as5048_read_register(as5048_handle_t handle, uint16_t reg_addr, uint16_t *out_val)
{
    uint16_t tx_cmd = AS5048_FRAME_READ_BIT | (reg_addr & AS5048_DATA_MASK);
    uint16_t rx_prev = 0;
    uint16_t rx_data = 0;

    // 1-ий кадр: передача команди читання обраного регістра
    esp_err_t ret = as5048_spi_transfer(handle, tx_cmd, &rx_prev);
    if (ret != ESP_OK) {
        return ret;
    }

    // 2-ий кадр: передача NOP для вичитування відповіді на запит
    uint16_t nop_cmd = AS5048_FRAME_READ_BIT | AS5048_REG_NOP;
    ret = as5048_spi_transfer(handle, nop_cmd, &rx_data);
    if (ret != ESP_OK) {
        return ret;
    }

    // Перевірка наявності прапорця помилки EF (біт 14 у відповіді)
    if (rx_data & AS5048_FRAME_EF_BIT) {
        ESP_LOGW(TAG, "Прапорець EF встановлено у відповіді. Скидання та читання ERRFL...");
        uint16_t err_flags = 0;
        as5048_read_error(handle, &err_flags);
        return ESP_ERR_INVALID_STATE;
    }

    if (out_val) {
        *out_val = rx_data & AS5048_DATA_MASK;
    }

    return ESP_OK;
}

esp_err_t as5048_init(const as5048_config_t *config, as5048_handle_t *out_handle)
{
    if (!config || !out_handle) {
        return ESP_ERR_INVALID_ARG;
    }

    as5048_handle_t dev = (as5048_handle_t)calloc(1, sizeof(struct as5048_dev_s));
    if (!dev) {
        return ESP_ERR_NO_MEM;
    }

    dev->cs_io_num = config->cs_io_num;
    dev->zero_offset = config->zero_offset & AS5048_DATA_MASK;

    spi_device_interface_config_t devcfg = {
        .command_bits = 0,
        .address_bits = 0,
        .dummy_bits = 0,
        .mode = 1, // SPI Mode 1 (CPOL=0, CPHA=1) відповідно до специфікації AS5048
        .clock_speed_hz = (config->clock_speed_hz > 0) ? config->clock_speed_hz : 1000000,
        .spics_io_num = config->cs_io_num,
        .queue_size = 7
    };

    esp_err_t ret = spi_bus_add_device(config->spi_host, &devcfg, &dev->spi_dev);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося додати пристрій SPI: %s", esp_err_to_name(ret));
        free(dev);
        return ret;
    }

    *out_handle = dev;

    // Скидаємо початкові прапорці помилок, якщо вони були присутні
    uint16_t dummy_err = 0;
    as5048_read_error(dev, &dummy_err);

    return ESP_OK;
}

esp_err_t as5048_deinit(as5048_handle_t handle)
{
    if (!handle) {
        return ESP_ERR_INVALID_ARG;
    }

    if (handle->spi_dev) {
        spi_bus_remove_device(handle->spi_dev);
    }
    free(handle);
    return ESP_OK;
}

esp_err_t as5048_read_raw_angle(as5048_handle_t handle, uint16_t *out_raw_angle)
{
    if (!handle || !out_raw_angle) {
        return ESP_ERR_INVALID_ARG;
    }

    return as5048_read_register(handle, AS5048_REG_ANGLE, out_raw_angle);
}

esp_err_t as5048_read_angle(as5048_handle_t handle, float *out_degrees)
{
    if (!handle || !out_degrees) {
        return ESP_ERR_INVALID_ARG;
    }

    uint16_t raw_angle = 0;
    esp_err_t ret = as5048_read_raw_angle(handle, &raw_angle);
    if (ret != ESP_OK) {
        return ret;
    }

    // Програмна корекція зсуву нульової позиції: (raw - zero_offset) & 0x3FFF
    int32_t corrected = (int32_t)raw_angle - (int32_t)handle->zero_offset;
    if (corrected < 0) {
        corrected += AS5048_MAX_RAW_ANGLE;
    }
    corrected &= AS5048_DATA_MASK;

    *out_degrees = as5048_raw_to_degrees((uint16_t)corrected);
    return ESP_OK;
}

esp_err_t as5048_set_zero_offset(as5048_handle_t handle, uint16_t zero_offset)
{
    if (!handle) {
        return ESP_ERR_INVALID_ARG;
    }
    handle->zero_offset = zero_offset & AS5048_DATA_MASK;
    return ESP_OK;
}

esp_err_t as5048_calibrate_zero(as5048_handle_t handle)
{
    if (!handle) {
        return ESP_ERR_INVALID_ARG;
    }

    uint16_t current_raw = 0;
    esp_err_t ret = as5048_read_raw_angle(handle, &current_raw);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося зчитати кут для калібрування нуля");
        return ret;
    }

    handle->zero_offset = current_raw;
    ESP_LOGI(TAG, "Встановлено новий zero_offset = %u (0x%04X)", current_raw, current_raw);
    return ESP_OK;
}

esp_err_t as5048_get_diagnostics(as5048_handle_t handle, as5048_diag_status_t *out_diag)
{
    if (!handle || !out_diag) {
        return ESP_ERR_INVALID_ARG;
    }

    uint16_t reg_val = 0;
    esp_err_t ret = as5048_read_register(handle, AS5048_REG_AGC_DIAG, &reg_val);
    if (ret != ESP_OK) {
        return ret;
    }

    out_diag->agc_val = (uint8_t)(reg_val & AS5048_AGC_MASK);
    out_diag->ocf = (reg_val & AS5048_DIAG_OCF) != 0;
    out_diag->cof = (reg_val & AS5048_DIAG_COF) != 0;
    out_diag->magl = (reg_val & AS5048_DIAG_MAGL) != 0;
    out_diag->magh = (reg_val & AS5048_DIAG_MAGH) != 0;

    return ESP_OK;
}

esp_err_t as5048_read_error(as5048_handle_t handle, uint16_t *out_error_flags)
{
    if (!handle) {
        return ESP_ERR_INVALID_ARG;
    }

    uint16_t tx_cmd = AS5048_FRAME_READ_BIT | AS5048_REG_ERRFL;
    uint16_t dummy = 0;
    uint16_t rx_err = 0;

    // Надсилаємо запит на читання регістра ERRFL
    esp_err_t ret = as5048_spi_transfer(handle, tx_cmd, &dummy);
    if (ret != ESP_OK) {
        return ret;
    }

    // Отримуємо значення регістра ERRFL через NOP
    uint16_t nop_cmd = AS5048_FRAME_READ_BIT | AS5048_REG_NOP;
    ret = as5048_spi_transfer(handle, nop_cmd, &rx_err);
    if (ret != ESP_OK) {
        return ret;
    }

    uint16_t err_mask = rx_err & AS5048_DATA_MASK;
    if (out_error_flags) {
        *out_error_flags = err_mask;
    }

    if (err_mask & AS5048_ERR_FRAMING) {
        ESP_LOGE(TAG, "Помилка ERRFL: Framing error (некоректні такти SPI)");
    }
    if (err_mask & AS5048_ERR_INVALID_CMD) {
        ESP_LOGE(TAG, "Помилка ERRFL: Command invalid (невідома команда/адреса)");
    }
    if (err_mask & AS5048_ERR_PARITY) {
        ESP_LOGE(TAG, "Помилка ERRFL: Parity error (збій парності команди)");
    }

    return ESP_OK;
}

float as5048_raw_to_degrees(uint16_t raw_angle)
{
    return ((float)(raw_angle & AS5048_DATA_MASK) * 360.0f) / (float)AS5048_MAX_RAW_ANGLE;
}
