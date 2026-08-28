#ifndef BLACKBODY_RADIATION_H
#define BLACKBODY_RADIATION_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Статуси виконання обчислювальних операцій */
typedef enum {
    BB_SUCCESS = 0,
    BB_ERROR_INVALID_TEMP = -1,
    BB_ERROR_INVALID_WAVELENGTH = -2,
    BB_ERROR_INVALID_RANGE = -3,
    BB_ERROR_OVERFLOW = -4,
    BB_ERROR_INTEGRATION_FAILED = -5
} bb_status_t;

#ifdef __cplusplus
}
#endif

#endif /* BLACKBODY_RADIATION_H */
