#ifndef BRIDGE_CORE_H
#define BRIDGE_CORE_H

#include <stdint.h>
#include <stddef.h>

#ifdef _WIN32
  #define BRIDGE_API __declspec(dllexport)
#else
  #define BRIDGE_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок операцій */
typedef enum {
    BRIDGE_OK = 0,
    BRIDGE_ERR_NULL_PTR = 1,
    BRIDGE_ERR_INVALID_PARAM = 2,
    BRIDGE_ERR_OUT_OF_MEMORY = 3,
    BRIDGE_ERR_COMPUTATION = 4
} BridgeStatus;

/* Структура конфігурації з явним вирівнюванням */
typedef struct {
    int32_t sample_rate;    /* 4 байти, зміщення 0 */
    int32_t channels;       /* 4 байти, зміщення 4 */
    double  scale_factor;   /* 8 байтів, зміщення 8 (вирівняно по 8) */
    uint8_t enable_filter;  /* 1 байт, зміщення 16 */
    uint8_t padding[7];     /* 7 байтів явної набивки до загального розміру 24 байти */
} BridgeConfig;

/* Непрозорий тип контексту обробки */
typedef struct BridgeContext BridgeContext;

/* Життєвий цикл контексту: створення, обробка, знищення */
BRIDGE_API BridgeStatus bridge_create_context(const BridgeConfig *config, BridgeContext **out_ctx);
BRIDGE_API BridgeStatus bridge_process_buffer(BridgeContext *ctx, const float *input, size_t count, float **out_buf, size_t *out_count);
BRIDGE_API void         bridge_free_buffer(float *buf);
BRIDGE_API void         bridge_free_context(BridgeContext *ctx);
BRIDGE_API const char*  bridge_get_last_error(BridgeStatus status);

#ifdef __cplusplus
}
#endif

#endif /* BRIDGE_CORE_H */
