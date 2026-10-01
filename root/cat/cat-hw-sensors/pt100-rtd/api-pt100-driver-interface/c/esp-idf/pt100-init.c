#include <stdint.h>
#include <stdbool.h>

typedef enum {
    PT100_WIRE_2 = 2,
    PT100_WIRE_3 = 3,
    PT100_WIRE_4 = 4
} pt100_wire_mode_t;

typedef enum {
    PT100_CLASS_A,
    PT100_CLASS_B
} pt100_class_t;

typedef struct {
    pt100_wire_mode_t wire_mode;   // Схема підключення (2, 3 або 4 дроти)
    pt100_class_t sensor_class;    // Клас точності елемента
    float r_ref_ohms;              // Опір опорного резистора (Ом)
    float excitation_current_ua;   // Струм збудження (мкА)
    uint8_t adc_resolution_bits;   // Розрядність АЦП у бітах
} pt100_config_t;

typedef struct {
    pt100_config_t config;
    bool is_initialized;
} pt100_t;

int pt100_init(pt100_t *dev, const pt100_config_t *cfg) {
    if (!dev || !cfg || cfg->r_ref_ohms <= 0.0f) {
        return -1; // Некоректні параметри
    }
    dev->config = *cfg;
    dev->is_initialized = true;
    return 0; // Успішна ініціалізація
}
