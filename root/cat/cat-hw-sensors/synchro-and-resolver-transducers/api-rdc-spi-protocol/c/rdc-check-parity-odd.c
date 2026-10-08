#include <stdint.h>
#include <stdbool.h>

#define RDC_MASK_LOS       (1U << 0)
#define RDC_MASK_DOS       (1U << 1)
#define RDC_MASK_LOT       (1U << 2)

typedef enum {
    RDC_STATUS_OK = 0,
    RDC_STATUS_ERR_PARITY,
    RDC_STATUS_ERR_LOS,
    RDC_STATUS_ERR_LOT,
    RDC_STATUS_WARN_DOS
} rdc_status_t;

typedef struct {
    float angle_rad;
    float velocity_rad_s;
    rdc_status_t status;
    uint32_t parity_error_count;
} rdc_measurement_t;

// Платформозалежні апаратні функції (інтерфейс HAL/LL)
extern void rdc_hal_set_sample_pin(bool state);
extern void rdc_hal_set_cs_pin(bool state);
extern void rdc_hal_delay_ns(uint32_t ns);
extern uint16_t rdc_hal_spi_transfer16(uint16_t tx_data);

static inline bool rdc_check_parity_odd(uint16_t frame) {
    uint16_t temp = frame;
    temp ^= temp >> 8;
    temp ^= temp >> 4;
    temp ^= temp >> 2;
    temp ^= temp >> 1;
    return (temp & 0x0001) != 0;
}

rdc_status_t rdc_read_data(rdc_measurement_t *out_data, float max_velocity_rad_s) {
    if (!out_data) {
        return RDC_STATUS_ERR_PARITY;
    }

    // 1. Стробування лінії SAMPLE для фіксації аналогового стану
    rdc_hal_set_sample_pin(false);
    rdc_hal_delay_ns(500); // Затримка t_SAMPLE (500 нс)
    rdc_hal_set_sample_pin(true);

    // 2. Активація CS та послідовне читання регістрів
    rdc_hal_set_cs_pin(false);
    rdc_hal_delay_ns(100); // Затримка t_CS_SETUP

    uint16_t raw_pos_frame = rdc_hal_spi_transfer16(0x0000);
    uint16_t raw_vel_status_frame = rdc_hal_spi_transfer16(0x0000);

    rdc_hal_set_cs_pin(true);
    rdc_hal_delay_ns(500); // Пауза t_QUIET

    // 3. Контроль цілісності кадру по паритету
    if (!rdc_check_parity_odd(raw_pos_frame)) {
        out_data->parity_error_count++;
        out_data->status = RDC_STATUS_ERR_PARITY;
        return RDC_STATUS_ERR_PARITY;
    }

    // 4. Розбір критичних апаратних прапорців
    uint8_t fault_flags = (uint8_t)(raw_vel_status_frame & 0x00FF);
    if (fault_flags & RDC_MASK_LOS) {
        out_data->status = RDC_STATUS_ERR_LOS;
        return RDC_STATUS_ERR_LOS;
    }
    if (fault_flags & RDC_MASK_LOT) {
        out_data->status = RDC_STATUS_ERR_LOT;
        return RDC_STATUS_ERR_LOT;
    }

    // 5. Обчислення кута та швидкості
    uint16_t raw_pos = (raw_pos_frame >> 1) & 0x7FFF;
    out_data->angle_rad = ((float)raw_pos / 32768.0f) * 6.28318530718f;

    int16_t raw_vel = (int16_t)raw_vel_status_frame;
    out_data->velocity_rad_s = ((float)raw_vel / 32767.0f) * max_velocity_rad_s;

    if (fault_flags & RDC_MASK_DOS) {
        out_data->status = RDC_STATUS_WARN_DOS;
        return RDC_STATUS_WARN_DOS;
    }

    out_data->status = RDC_STATUS_OK;
    return RDC_STATUS_OK;
}
