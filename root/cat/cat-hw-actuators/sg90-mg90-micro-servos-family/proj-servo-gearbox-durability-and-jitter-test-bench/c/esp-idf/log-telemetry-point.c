#include <stdio.h>
#include "esp_timer.h"

typedef struct {
    uint32_t timestamp_ms;
    float target_angle_deg;
    float actual_angle_deg;
} telemetry_frame_t;

#define RING_BUFFER_SIZE 128
static telemetry_frame_t ring_buffer[RING_BUFFER_SIZE];
static volatile uint16_t head_idx = 0;
static volatile uint16_t tail_idx = 0;

void log_telemetry_point(float target_angle, float actual_angle) {
    uint16_t next_head = (head_idx + 1) % RING_BUFFER_SIZE;
    if (next_head != tail_idx) {
        ring_buffer[head_idx].timestamp_ms = (uint32_t)(esp_timer_get_time() / 1000);
        ring_buffer[head_idx].target_angle_deg = target_angle;
        ring_buffer[head_idx].actual_angle_deg = actual_angle;
        head_idx = next_head;
    }
}
