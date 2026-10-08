#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2c.h"
#include "esp_log.h"

#define I2C_MASTER_NUM         I2C_NUM_0
#define TOF_SENSOR_ADDR        0x29
#define FILTER_WINDOW_SIZE    5

static const char *TAG = "TOF_DRIVER";

typedef struct {
    uint16_t window[FILTER_WINDOW_SIZE];
    size_t count;
    size_t index;
    float ema_state;
    float alpha;
    bool initialized;
} tof_filter_t;

void tof_filter_init(tof_filter_t *filter, float alpha) {
    memset(filter, 0, sizeof(tof_filter_t));
    filter->alpha = alpha;
}

static int compare_uint16(const void *a, const void *b) {
    uint16_t arg1 = *(const uint16_t *)a;
    uint16_t arg2 = *(const uint16_t *)b;
    if (arg1 < arg2) return -1;
    if (arg1 > arg2) return 1;
    return 0;
}

uint16_t tof_filter_process(tof_filter_t *filter, uint16_t raw_sample) {
    filter->window[filter->index] = raw_sample;
    filter->index = (filter->index + 1) % FILTER_WINDOW_SIZE;
    if (filter->count < FILTER_WINDOW_SIZE) {
        filter->count++;
    }

    uint16_t tempbuf[FILTER_WINDOW_SIZE];
    memcpy(tempbuf, filter->window, filter->count * sizeof(uint16_t));
    qsort(tempbuf, filter->count, sizeof(uint16_t), compare_uint16);

    uint16_t median_val = tempbuf[filter->count / 2];

    if (!filter->initialized) {
        filter->ema_state = (float)median_val;
        filter->initialized = true;
    } else {
        filter->ema_state = filter->alpha * (float)median_val + (1.0f - filter->alpha) * filter->ema_state;
    }

    return (uint16_t)(filter->ema_state + 0.5f);
}

esp_err_t tof_read_distance_raw(uint16_t *distance_mm) {
    uint8_t reg_addr = 0x14;
    uint8_t data[2] = {0};

    esp_err_t err = i2c_master_write_read_device(I2C_MASTER_NUM, TOF_SENSOR_ADDR,
                                                &reg_addr, 1,
                                                data, 2,
                                                pdMS_TO_TICKS(100));
    if (err == ESP_OK) {
        *distance_mm = ((uint16_t)data[0] << 8) | data[1];
    }
    return err;
}

void app_main(void) {
    tof_filter_t filter;
    tof_filter_init(&filter, 0.25f);

    uint16_t raw_mm = 0;
    while (1) {
        if (tof_read_distance_raw(&raw_mm) == ESP_OK) {
            uint16_t filtered_mm = tof_filter_process(&filter, raw_mm);
            ESP_LOGI(TAG, "Raw: %u mm, Filtered: %u mm", raw_mm, filtered_mm);
        }
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
