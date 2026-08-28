// sensor.c  —  тіло сховане тут
#include "sensor.h"
#include <stdlib.h>

struct sensor {           // ← справжні поля, видно лише цьому файлу
    int      pin;
    float    scale, offset;
    uint16_t buf[64];
    uint32_t last_us;
};

sensor_t *sensor_open(int pin) {
    sensor_t *s = malloc(sizeof *s);   // sizeof знає повний тип — ми ж усередині
    if (!s) return NULL;
    s->pin = pin;
    s->scale = 1.0f; s->offset = 0.0f;
    s->last_us = 0;
    return s;
}

float sensor_read(sensor_t *s) {
    /* … читаємо АЦП, застосовуємо scale/offset … */
    return 0.0f;
}

void sensor_close(sensor_t *s) { free(s); }
