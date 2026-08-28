// PAL OSD Timing Calculation in C
#include <stdio.h>
#include <stdint.h>

void calculate_osd_timing(void) {
    const float active_time_sec = 52.0e-6f; // 52 мікросекунди
    const uint16_t active_pixels = 320;
    
    // Розрахунок частоти піксельного такту (Hz)
    float pixel_clock_hz = (float)active_pixels / active_time_sec;
    
    // Час одного пікселя (ns)
    float pixel_time_ns = (1.0f / pixel_clock_hz) * 1.0e9f;
    
    // Час передачі 1 байта (8 пікселів) через SPI (ns)
    float byte_time_ns = pixel_time_ns * 8.0f;

    printf("Pixel Clock: %.2f MHz\n", pixel_clock_hz / 1.0e6f);
    printf("Pixel Duration: %.1f ns\n", pixel_time_ns);
    printf("SPI Byte Duration: %.1f ns\n", byte_time_ns);
}
