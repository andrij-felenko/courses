#include "rvdt_rdc.h"
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

/// Допоміжна функція перевірки парності 16-бітного слова
static bool check_parity(uint16_t word) {
    uint16_t val = word;
    val ^= val >> 8;
    val ^= val >> 4;
    val ^= val >> 2;
    val ^= val >> 1;
    return (val & 1U) == 0U; // Парна кількість одиниць
}

rvdt_status_t rvdt_init(rvdt_handle_t *handle, const rvdt_config_t *config, rvdt_spi_transfer_fn spi_fn) {
    if (handle == NULL || config == NULL || spi_fn == NULL) {
        return RVDT_ERR_SPI_TIMEOUT;
    }

    handle->config = *config;
    handle->spi_transfer = spi_fn;
    handle->is_initialized = true;

    return RVDT_OK;
}

rvdt_status_t rvdt_read_angle(rvdt_handle_t *handle, rvdt_measurement_t *result) {
    if (handle == NULL || result == NULL || !handle->is_initialized) {
        return RVDT_ERR_SPI_TIMEOUT;
    }

    // Скидаємо вихідні дані
    result->raw_code = 0;
    result->angle_deg = 0.0f;
    result->angle_rad = 0.0f;
    result->rdc_status_flags = 0;
    result->driver_status = RVDT_OK;

    // 1. Апаратна SPI-транзакція (2 байти = 16 біт)
    uint8_t tx_data[2] = {0x00, 0x00};
    uint8_t rx_data[2] = {0x00, 0x00};

    bool spi_ok = handle->spi_transfer(handle->config.spi_channel,
                                       tx_data,
                                       rx_data,
                                       sizeof(rx_data),
                                       handle->config.timeout_us);

    if (!spi_ok) {
        result->driver_status = RVDT_ERR_SPI_TIMEOUT;
        return RVDT_ERR_SPI_TIMEOUT;
    }

    // Збірка 16-бітного кадру (MSB First)
    uint16_t raw_word = (uint16_t)((rx_data[0] << 8) | rx_data[1]);

    // 2. Перевірка контрольного біта парності (якщо підтримується схемотехнікою RDC)
    if (!check_parity(raw_word)) {
        result->driver_status = RVDT_ERR_PARITY;
        return RVDT_ERR_PARITY;
    }

    // 3. Виділення статусних бітів (Нижні біти D0-D2 містять прапорці аварій RDC)
    uint8_t rdc_flags = (uint8_t)(raw_word & 0x07U);
    result->rdc_status_flags = rdc_flags;

    if ((rdc_flags & RDC_STATUS_LOS_MASK) != 0U) {
        result->driver_status = RVDT_ERR_LOSS_OF_SIGNAL;
        return RVDT_ERR_LOSS_OF_SIGNAL; // Обрив/КЗ лінії RVDT
    }

    if ((rdc_flags & RDC_STATUS_DOS_MASK) != 0U) {
        result->driver_status = RVDT_ERR_SIGNAL_DEGRADED;
        return RVDT_ERR_SIGNAL_DEGRADED; // Зниження амплітуди
    }

    if ((rdc_flags & RDC_STATUS_LOT_MASK) != 0U) {
        result->driver_status = RVDT_ERR_TRACKING_LOST;
        return RVDT_ERR_TRACKING_LOST; // Помилка стеження
    }

    // 4. Маскування та зсув позиції залежно від обраної розрядності
    uint16_t raw_code = 0;
    uint32_t max_code = (1U << handle->config.resolution);

    switch (handle->config.resolution) {
        case RDC_RES_16_BIT:
            raw_code = raw_word;
            break;
        case RDC_RES_14_BIT:
            raw_code = (raw_word >> 2) & 0x3FFFU;
            break;
        case RDC_RES_12_BIT:
            raw_code = (raw_word >> 4) & 0x0FFFU;
            break;
        case RDC_RES_10_BIT:
            raw_code = (raw_word >> 6) & 0x03FFU;
            break;
        default:
            raw_code = (raw_word >> 4) & 0x0FFFU; // За замовчуванням 12 біт
            break;
    }

    result->raw_code = raw_code;

    // 5. Перерахунок сирого коду в кутові градуси [-180.0 .. +180.0]
    float raw_angle_deg = ((float)raw_code / (float)max_code) * 360.0f;
    if (raw_angle_deg > 180.0f) {
        raw_angle_deg -= 360.0f; // Нормалізація в симетричний діапазон
    }

    // Застосування компенсації нульового зсуву RVDT
    float final_deg = raw_angle_deg - handle->config.zero_offset_deg;

    // Обмеження нормалізованого кута
    if (final_deg > 180.0f) final_deg -= 360.0f;
    if (final_deg < -180.0f) final_deg += 360.0f;

    result->angle_deg = final_deg;
    result->angle_rad = final_deg * (M_PI / 180.0f);
    result->driver_status = RVDT_OK;

    return RVDT_OK;
}
