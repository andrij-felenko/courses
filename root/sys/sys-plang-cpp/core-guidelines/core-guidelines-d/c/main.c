/* Традиційний C-підхід: амбівалентне володіння, небезпечні масиви, коди помилок */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char* name;
    double* readings;
    int readings_count;
} SensorData;

SensorData* create_sensor(const char* name, const double* initial_data, int count) {
    if (!name || count < 0) return NULL;

    SensorData* s = (SensorData*)malloc(sizeof(SensorData));
    if (!s) return NULL;

    s->name = (char*)malloc(strlen(name) + 1);
    strcpy(s->name, name);

    if (count > 0 && initial_data) {
        s->readings = (double*)malloc(sizeof(double) * count);
        memcpy(s->readings, initial_data, sizeof(double) * count);
        s->readings_count = count;
    } else {
        s->readings = NULL;
        s->readings_count = 0;
    }
    return s;
}

void destroy_sensor(SensorData* s) {
    if (!s) return;
    free(s->name);
    free(s->readings);
    free(s);
}
