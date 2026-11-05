#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"

#define MAX_AXES 3
#define RING_BUFFER_SIZE 16

typedef struct {
    int32_t delta[MAX_AXES];
    int32_t accumulator[MAX_AXES];
    uint32_t step_mask[MAX_AXES];
    uint32_t dir_mask_set;
    uint32_t dir_mask_clr;
    uint8_t lead_axis;
    uint32_t total_steps;
    uint32_t current_step;
} dda_segment_t;

typedef struct {
    dda_segment_t buffer[RING_BUFFER_SIZE];
    volatile uint8_t head;
    volatile uint8_t tail;
} dda_ring_buffer_t;

static dda_ring_buffer_t ring_buf;

void IRAM_ATTR dda_timer_isr_handler(void* arg) {
    if (ring_buf.head == ring_buf.tail) {
        return;
    }

    dda_segment_t* seg = &ring_buf.buffer[ring_buf.tail];

    if (seg->current_step == 0) {
        GPIO.out_w1ts = seg->dir_mask_set;
        GPIO.out_w1tc = seg->dir_mask_clr;
    }

    if (seg->current_step < seg->total_steps) {
        uint32_t gpio_step_set = 0;

        for (uint8_t i = 0; i < MAX_AXES; i++) {
            if (i == seg->lead_axis) {
                gpio_step_set |= seg->step_mask[i];
            } else {
                seg->accumulator[i] += seg->delta[i];
                if (seg->accumulator[i] >= (int32_t)seg->total_steps) {
                    gpio_step_set |= seg->step_mask[i];
                    seg->accumulator[i] -= seg->total_steps;
                }
            }
        }

        GPIO.out_w1ts = gpio_step_set;
        GPIO.out_w1tc = gpio_step_set;
        seg->current_step++;
    } else {
        ring_buf.tail = (ring_buf.tail + 1) % RING_BUFFER_SIZE;
    }
}
