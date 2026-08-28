/* sensor.c — прихована таємниця на C */
#include "sensor.h"
#include <stdlib.h>

struct sensor {
    uint8_t  bus_id;
    uint32_t calibration_raw[16];
    float    last_reading;
    void    *spi_handle;
};

sensor_t* sensor_create(uint8_t bus_id) {
    sensor_t *s = (sensor_t*)malloc(sizeof(struct sensor));
    if (!s) return NULL;
    s->bus_id = bus_id;
    s->last_reading = 0.0f;
    return s;
}

int sensor_read_temperature(sensor_t *s, float *out_temp) {
    if (!s || !out_temp) return -1;
    *out_temp = s->last_reading;
    return 0;
}

void sensor_destroy(sensor_t *s) {
    free(s);
}
