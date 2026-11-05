#ifndef DIGIMATIC_H
#define DIGIMATIC_H

#include <stdint.h>
#include <stdbool.h>

#define DIGIMATIC_NIBBLES 13

typedef struct {
    uint8_t d[DIGIMATIC_NIBBLES];
} digimatic_raw_frame_t;

typedef struct {
    bool valid;
    bool is_negative;
    uint32_t value_bcd;
    uint8_t decimal_point;
    bool is_inch;
} digimatic_measurement_t;

void digimatic_init(void);
void digimatic_request_measurement(void);
bool digimatic_is_ready(void);
digimatic_measurement_t digimatic_read_measurement(void);

#endif // DIGIMATIC_H
