#include <stdint.h>
#include <stddef.h>

// Нормалізація та масштабування PCM-буфера у Q15 арифметиці
void normalize_pcm_buffer(int16_t *buffer, size_t count, int32_t gain_q15) {
    if (buffer == NULL || count == 0) {
        return;
    }

    for (size_t i = 0; i < count; i++) {
        int32_t scaled = ((int32_t)buffer[i] * gain_q15) >> 15;
        
        // Арифметика насичення (saturation clamping)
        if (scaled > 32767) {
            scaled = 32767;
        } else if (scaled < -32768) {
            scaled = -32768;
        }
        
        buffer[i] = (int16_t)scaled;
    }
}
