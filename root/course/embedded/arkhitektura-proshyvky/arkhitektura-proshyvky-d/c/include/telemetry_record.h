/* include/telemetry_record.h — контракт даних між застосунком і портом.
 * Запис телеметрії народжується в шарі застосунку, а споживає його
 * платформозалежний код: передавач UART на платі, друк у консоль на
 * комп'ютері розробника. Тип лежить у include/, щоб порт не мусив
 * включати заголовки застосунку й потік залежностей лишався вниз. */
#ifndef TELEMETRY_RECORD_H
#define TELEMETRY_RECORD_H

#include <stdint.h>

typedef struct {
    uint32_t window_start_ms;
    uint32_t window_end_ms;
    uint32_t sample_count;
    float    temp_avg_c;
    float    temp_min_c;
    float    temp_max_c;
    float    humidity_avg_rh;
    float    pressure_avg_hpa;
    float    vibration_rms_g;
    float    vibration_peak_g;
    uint32_t fault_count;
} telemetry_record_t;

/* Приймач готового запису. Реалізацію дає порт. */
typedef void (*telemetry_sink_fn)(void *ctx, const telemetry_record_t *rec);

#endif /* TELEMETRY_RECORD_H */
