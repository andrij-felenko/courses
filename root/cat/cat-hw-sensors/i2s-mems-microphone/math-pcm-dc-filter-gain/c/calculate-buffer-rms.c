#include <stdint.h>
#include <stddef.h>
#include <math.h>

// Обчислення RMS-рівня для 16-бітного PCM-буфера
uint16_t calculate_buffer_rms(const int16_t *buffer, size_t count) {
    if (buffer == NULL || count == 0) {
        return 0;
    }
    
    uint64_t sum_squares = 0;
    for (size_t i = 0; i < count; i++) {
        int32_t sample = buffer[i];
        sum_squares += (uint64_t)(sample * sample);
    }
    
    uint64_t mean_square = sum_squares / count;
    return (uint16_t)sqrt((double)mean_square);
}
