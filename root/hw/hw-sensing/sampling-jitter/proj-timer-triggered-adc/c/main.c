/* Еквівалентна структура на чистому C */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define ADC_BUFFER_SIZE 2048
#define ADC_HALF_SIZE   (ADC_BUFFER_SIZE / 2)

typedef struct {
    uint16_t buffer[ADC_BUFFER_SIZE] __attribute__((aligned(32)));
    volatile bool half_ready;
    volatile bool full_ready;
} AdcDoubleBuffer_t;

static AdcDoubleBuffer_t g_adc_buf;

void AdcBuffer_Init(AdcDoubleBuffer_t* buf) {
    buf->half_ready = false;
    buf->full_ready = false;
}

void AdcBuffer_OnHalfISR(AdcDoubleBuffer_t* buf) {
    buf->half_ready = true;
}

void AdcBuffer_OnFullISR(AdcDoubleBuffer_t* buf) {
    buf->full_ready = true;
}

void AdcBuffer_Process(AdcDoubleBuffer_t* buf, void (*process_fn)(const uint16_t* data, size_t len)) {
    if (buf->half_ready) {
        buf->half_ready = false;
        process_fn(&buf->buffer[0], ADC_HALF_SIZE);
    }
    if (buf->full_ready) {
        buf->full_ready = false;
        process_fn(&buf->buffer[ADC_HALF_SIZE], ADC_HALF_SIZE);
    }
}
