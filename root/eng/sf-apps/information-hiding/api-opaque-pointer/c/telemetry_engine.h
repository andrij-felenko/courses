/* telemetry_engine.h — публічний контракт модуля */
#ifndef TELEMETRY_ENGINE_H
#define TELEMETRY_ENGINE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Неповний тип: компілятор знає лише про існування імені типу */
typedef struct telemetry_engine telemetry_engine_t;

/* Коди результату виконання операцій (статус-контракт) */
typedef enum {
    TE_OK              =  0,
    TE_ERR_INVALID_ARG = -1,
    TE_ERR_NO_MEMORY   = -2,
    TE_ERR_OVERFLOW    = -3,
    TE_ERR_HARDWARE_IO = -4
} te_status_t;

/* Публічна конфігурація для створення екземпляра */
typedef struct {
    uint32_t sample_rate_hz;
    size_t   max_channels;
} te_config_t;

/* =========================================================================
 * Керування життєвим циклом (Lifecycle)
 * ========================================================================= */

/**
 * Створює новий екземпляр модуля телеметрії.
 * Виділяє пам'ять під повну структуру всередині файлу реалізації.
 * Повертає покажчик на екземпляр або NULL при нестачі пам'яті / некоректних параметрах.
 */
telemetry_engine_t* te_create(const te_config_t *config);

/**
 * Знищує екземпляр, звільняє всі внутрішні ресурси та пам'ять.
 * Безпечно приймати NULL (операція no-op).
 */
void te_destroy(telemetry_engine_t *engine);

/* =========================================================================
 * Публічні операції над станом (Operations)
 * ========================================================================= */

/**
 * Записує виміряне значення у вказаний канал телеметрії.
 * Передумови: engine != NULL, channel_id < max_channels.
 * Постумова: значення додано у внутрішній кільцевий буфер, оновлено суму.
 */
te_status_t te_push_sample(telemetry_engine_t *engine, uint16_t channel_id, float value);

/**
 * Обчислює поточне ковзне середнє для вказаного каналу.
 * Результат записується у *out_mean.
 */
te_status_t te_get_channel_mean(const telemetry_engine_t *engine, uint16_t channel_id, float *out_mean);

/**
 * Скидає накопичену історію всіх каналів без перерозподілу пам'яті.
 */
te_status_t te_reset(telemetry_engine_t *engine);

#ifdef __cplusplus
}
#endif

#endif /* TELEMETRY_ENGINE_H */
