#include <stdint.h>
#include <stdbool.h>

// Стан драйвера RVDT
typedef enum {
    RVDT_OK = 0,
    RVDT_ERR_SIGNAL_LOW = 1,
    RVDT_ERR_SIGNAL_HIGH = 2,
    RVDT_ERR_PHASE_SYNC = 3
} rvdt_status_t;

// Конфігурація драйвера
typedef struct {
    uint32_t sample_rate_hz;     // Частота дискретизації АЦП
    uint32_t carrier_freq_hz;    // Частота збудження
    float    lpf_cutoff_hz;      // Частота зрізу ФНЧ
    float    scale_factor;       // Коефіцієнт масштабування кута
} rvdt_config_t;

// Кадр оброблених даних
typedef struct {
    float    raw_v1_rms;         // СКЗ напруги першої обмотки
    float    raw_v2_rms;         // СКЗ напруги другої обмотки
    float    demod_v1;           // Демодульована огинаюча V1
    float    demod_v2;           // Демодульована огинаюча V2
    float    calculated_angle;   // Обчислений кут у градусах
    rvdt_status_t status;        // Статус діагностики
} rvdt_handle_t;

// Ініціалізація драйвера
rvdt_status_t rvdt_init(rvdt_handle_t *handle, const rvdt_config_t *config);
