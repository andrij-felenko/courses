#pragma once

#include <cstdint>

namespace esp32_cam {

// Структура констант апаратного призначення виводів (GPIO) плати ESP32-CAM
struct CameraPins {
    // Сигнали керування живленням та скидання
    static constexpr int pwdn  = 32;
    static constexpr int reset = -1; // Апаратне скидання не задіяне

    // Сигнали тактування
    static constexpr int xclk  = 0;  // Тактова частота камери (XCLK)
    static constexpr int pclk  = 22; // Піксельне тактування (PCLK)

    // Послідовна шина SCCB (I2C)
    static constexpr int siod  = 26; // Дані SCCB (SDA)
    static constexpr int sioc  = 27; // Тактування SCCB (SCL)

    // 8-бітна паралельна шина даних D0–D7
    static constexpr int d7    = 35;
    static constexpr int d6    = 34;
    static constexpr int d5    = 39;
    static constexpr int d4    = 36;
    static constexpr int d3    = 21;
    static constexpr int d2    = 19;
    static constexpr int d1    = 18;
    static constexpr int d0    = 5;

    // Сигнали синхронізації
    static constexpr int vsync = 25; // Кадрова синхронізація
    static constexpr int href  = 23; // Рядкова синхронізація
};

} // namespace esp32_cam
