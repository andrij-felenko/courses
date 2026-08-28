#include <stdint.h>

typedef struct {
    uint16_t max, min;        // крайні значення
    uint16_t imax, imin;      // індекси відліків, де вони сталися
    uint16_t range;           // розмах max − min (peak-to-peak)
} stream_stats_t;

stream_stats_t scan_stream(const uint16_t *x, uint16_t n) {
    stream_stats_t s;
    s.max = s.min = x[0];     // ПОЧАТОК — з першого відліку, не з 0 і не з 0xFFFF
    s.imax = s.imin = 0;
    for (uint16_t i = 1; i < n; ++i) {
        if (x[i] > s.max) { s.max = x[i]; s.imax = i; }   // «A > B» на максимум
        else if (x[i] < s.min) { s.min = x[i]; s.imin = i; }  // «A < B» на мінімум
    }
    s.range = (uint16_t)(s.max - s.min);
    return s;
}
