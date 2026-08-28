// C99: Публічний контракт заголовного файлу драйвера
#ifndef CHIP_DRIVER_API_H
#define CHIP_DRIVER_API_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    chip_bus_read_fn  read;
    chip_bus_write_fn write;
    chip_delay_ms_fn  delay_ms;
} chip_bus_ops_t;

typedef struct {
    const chip_bus_ops_t *bus_ops;
    void                 *user_ctx;
    uint8_t               dev_addr;
    uint8_t               active_range;
    float                 scale_factor;
    uint8_t               shadow_ctrl_reg;
    bool                  is_initialized;
} chip_dev_t;

typedef struct {
    float x;  ///< Прискорення по осі X у м/с²
    float y;  ///< Прискорення по осі Y у м/с²
    float z;  ///< Прискорення по осі Z у м/с²
} chip_axes_data_si_t;

// Публічний контракт життєвого циклу
chip_status_t chip_init(chip_dev_t *dev, const chip_bus_ops_t *bus_ops, void *user_ctx, uint8_t dev_addr);
chip_status_t chip_set_range(chip_dev_t *dev, uint8_t range_g);
chip_status_t chip_read_sample_si(chip_dev_t *dev, chip_axes_data_si_t *data_si);
chip_status_t chip_soft_reset(chip_dev_t *dev);

#ifdef __cplusplus
}
#endif

#endif // CHIP_DRIVER_API_H
