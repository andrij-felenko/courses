#include <stdint.h>
#include <stdbool.h>

#define PCM24_MAX  8388607
#define PCM24_MIN -8388608

// Перевірка допустимості часових параметрів DMA в ESP32
bool verify_i2s_dma_timing(uint32_t sample_rate, uint16_t buffer_samples, uint32_t max_allowed_latency_us) {
    uint32_t buffer_time_us = (uint32_t)(((uint64_t)buffer_samples * 1000000ULL) / sample_rate);
    return buffer_time_us > max_allowed_latency_us;
}

// Запобігання кліпінгу за допомогою насиченої арифметики (Saturating Add)
int32_t pcm24_saturating_add(int32_t sample_a, int32_t sample_b) {
    int64_t sum = (int64_t)sample_a + (int64_t)sample_b;
    if (sum > PCM24_MAX) {
        return PCM24_MAX;
    }
    if (sum < PCM24_MIN) {
        return PCM24_MIN;
    }
    return (int32_t)sum;
}
