// system_clock.hpp (C++20)
#pragma once

struct ClockConfig {
    unsigned long default_frequency_hz;
    constexpr ClockConfig(unsigned long freq) : default_frequency_hz(freq) {}
};

// constinit гарантує: змінна ініціалізується до запуску будь-якого динамічного коду!
// Якщо конструктор не є constexpr — компілятор видасть помилку збірки.
constinit inline ClockConfig g_clock_config{16'000'000};
