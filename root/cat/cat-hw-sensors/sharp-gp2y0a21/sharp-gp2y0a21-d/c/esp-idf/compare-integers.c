#include <stdio.h>
#include <stdlib.h>
#include "esp_adc/adc_oneshot.h"

#define MEDIAN_WINDOW 5

static int compare_integers(const void *a, const void *b) {
    return (*(int *)a - *(int *)b);
}

int read_median_adc(adc_oneshot_unit_handle_t handle, adc_channel_t channel) {
    int samples[MEDIAN_WINDOW];
    for (int i = 0; i < MEDIAN_WINDOW; i++) {
        adc_oneshot_read(handle, channel, &samples[i]);
    }
    qsort(samples, MEDIAN_WINDOW, sizeof(int), compare_integers);
    return samples[MEDIAN_WINDOW / 2];
}

float calculate_distance_cm(int raw_adc) {
    if (raw_adc < 80) return -1.0f; // За межами робочого діапазону (>80 см)
    float distance = 6787.0f / ((float)raw_adc - 3.0f) - 4.0f;
    return (distance < 10.0f) ? 10.0f : distance;
}
