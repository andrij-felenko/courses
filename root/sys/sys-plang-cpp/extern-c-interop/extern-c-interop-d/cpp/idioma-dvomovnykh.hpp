#ifndef ENGINE_API_H
#define ENGINE_API_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Оголошення C-сумісних типів та сигнатур функцій */
typedef struct engine_t engine_t;

int  engine_init(engine_t** out_engine, const char* config);
void engine_release(engine_t* engine);

#ifdef __cplusplus
}
#endif

#endif /* ENGINE_API_H */
