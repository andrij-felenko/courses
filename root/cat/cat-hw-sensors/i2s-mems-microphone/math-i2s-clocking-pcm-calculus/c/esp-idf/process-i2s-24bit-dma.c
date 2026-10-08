#include <stdint.h>
#include <stddef.h>

// Розпакування 24-бітних PCM-семплів із 32-бітних слів DMA-буфера в ESP32
void process_i2s_24bit_dma(const uint32_t *dma_buffer, int32_t *out_samples, size_t sample_count) {
    for (size_t i = 0; i < sample_count; ++i) {
        uint32_t raw_word = dma_buffer[i];
        // 24-бітні дані розташовані в молодших 24 бітах (right-aligned)
        int32_t sample = (int32_t)(raw_word & 0x00FFFFFF);
        // Знакове розширення: якщо біт 23 встановлено (від'ємне число)
        if (sample & 0x00800000) {
            sample |= 0xFF000000;
        }
        out_samples[i] = sample;
    }
}
