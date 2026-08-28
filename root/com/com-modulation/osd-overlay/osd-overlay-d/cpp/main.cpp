// PAL OSD Timing Calculation in C++
#include <iostream>
#include <iomanip>

struct OsdTimingResult {
    double pixel_clock_mhz;
    double pixel_time_ns;
    double byte_time_ns;
};

constexpr OsdTimingResult computePalOsdTiming(uint16_t active_pixels = 320) noexcept {
    constexpr double kActiveTimeSec = 52.0e-6;
    const double pixel_clock_hz = static_cast<double>(active_pixels) / kActiveTimeSec;
    const double pixel_time_ns  = (1.0 / pixel_clock_hz) * 1.0e9;
    const double byte_time_ns   = pixel_time_ns * 8.0;

    return { pixel_clock_hz / 1.0e6, pixel_time_ns, byte_time_ns };
}
