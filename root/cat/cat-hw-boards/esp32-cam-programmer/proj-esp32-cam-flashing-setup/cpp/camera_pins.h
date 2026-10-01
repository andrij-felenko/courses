#ifndef CAMERA_PINS_H
#define CAMERA_PINS_H

// ============================================================================
// Призначення виводів GPIO для модуля AI-Thinker ESP32-CAM з сенсором OV2640.
// Стандартне розпінування плат ESP32-CAM при підключенні через Type-C / CH340.
// ============================================================================

// Лінії керування живленням та тактуванням
constexpr int PWDN_GPIO_NUM  = 32; // Сигнал вимкнення живлення камери (Power Down)
constexpr int RESET_GPIO_NUM = -1; // Скидання апаратне (не підключено на AI-Thinker)
constexpr int XCLK_GPIO_NUM  = 0;  // Тактовий сигнал камери (Master Clock)
constexpr int SIOD_GPIO_NUM  = 26; // Інтерфейс SCCB / I2C Data
constexpr int SIOC_GPIO_NUM  = 27; // Інтерфейс SCCB / I2C Clock

// Паралельні лінії даних зображення (D7..D0)
constexpr int Y9_GPIO_NUM    = 35; // D7
constexpr int Y8_GPIO_NUM    = 34; // D6
constexpr int Y7_GPIO_NUM    = 39; // D5
constexpr int Y6_GPIO_NUM    = 36; // D4
constexpr int Y5_GPIO_NUM    = 21; // D3
constexpr int Y4_GPIO_NUM    = 19; // D2
constexpr int Y3_GPIO_NUM    = 18; // D1
constexpr int Y2_GPIO_NUM    = 5;  // D0

// Сигнали синхронізації
constexpr int VSYNC_GPIO_NUM = 25; // Вертикальна синхронізація кадрів
constexpr int HREF_GPIO_NUM  = 23; // Горизонтальна синхронізація рядків
constexpr int PCLK_GPIO_NUM  = 22; // Тактування пікселів

// Допоміжні периферійні виводи
constexpr int FLASH_LED_GPIO = 4;  // Вбудований потужний світлодіод спалаху

#endif // CAMERA_PINS_H
