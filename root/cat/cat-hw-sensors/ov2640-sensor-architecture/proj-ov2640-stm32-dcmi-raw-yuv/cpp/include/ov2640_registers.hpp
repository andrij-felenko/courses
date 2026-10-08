#ifndef OV2640_REGISTERS_HPP
#define OV2640_REGISTERS_HPP

#include <cstdint>
#include <cstddef>

namespace ov2640 {

// Системні адреси банків регістрів
constexpr uint8_t BANK_DSP    = 0x00;
constexpr uint8_t BANK_SENSOR = 0x01;

// Адреса регістра вибору банку
constexpr uint8_t REG_BANK_SEL = 0xFF;

// Очікувані значення ідентифікаторів пристрою
constexpr uint8_t OV2640_EXPECTED_PID = 0x26;
constexpr uint8_t OV2640_EXPECTED_VER = 0x42;

// --- Сенсорний банк регістрів (Bank 0x01) ---
constexpr uint8_t REG_SENSOR_GAIN     = 0x00; // Підсилення AGC
constexpr uint8_t REG_SENSOR_BLUE     = 0x01; // Синій канал AWB
constexpr uint8_t REG_SENSOR_RED      = 0x02; // Червоний канал AWB
constexpr uint8_t REG_SENSOR_GREEN    = 0x03; // Зелений канал AWB
constexpr uint8_t REG_SENSOR_COM1     = 0x04; // Керування розміром кадру та каналом
constexpr uint8_t REG_SENSOR_BAVG     = 0x05;
constexpr uint8_t REG_SENSOR_PID      = 0x0A; // Ідентифікатор продукту (PID = 0x26)
constexpr uint8_t REG_SENSOR_VER      = 0x0B; // Версія продукту (VER = 0x42)
constexpr uint8_t REG_SENSOR_COM3     = 0x0C; // Режим виходу та тактування
constexpr uint8_t REG_SENSOR_AEC      = 0x10; // Автоекспозиція (молодші біти)
constexpr uint8_t REG_SENSOR_CLKRC    = 0x11; // Дільник тактової частоти камери (XCLK / internal CLK)
constexpr uint8_t REG_SENSOR_COM7     = 0x12; // Скидання пристрою та вибір вихідного формату
constexpr uint8_t REG_SENSOR_COM8     = 0x13; // Управління AGC/AEC/AWB
constexpr uint8_t REG_SENSOR_COM10    = 0x15; // Полярність сигналів PCLK, HREF, VSYNC
constexpr uint8_t REG_SENSOR_MIDH     = 0x1C; // Ідентифікатор виробника (High = 0x7F)
constexpr uint8_t REG_SENSOR_MIDL     = 0x1D; // Ідентифікатор виробника (Low = 0xA2)

// Маски та прапорці регістрів сенсора
constexpr uint8_t COM7_SOFT_RESET     = 0x80; // Біт програмного скидання
constexpr uint8_t COM7_RES_UXGA       = 0x00; // Режим UXGA (1600x1200)
constexpr uint8_t COM7_RES_SVGA       = 0x40; // Режим SVGA (800x600)
constexpr uint8_t COM7_RES_CIF        = 0x20; // Режим CIF (352x288)

// --- DSP банк регістрів (Bank 0x00) ---
constexpr uint8_t REG_DSP_R_BYPASS    = 0x05; // Обхід DSP блоку
constexpr uint8_t REG_DSP_QS          = 0x44; // Коефіцієнт квантування JPEG (0x00..0x3F)
constexpr uint8_t REG_DSP_CTRL0       = 0x2C; // Контролер форматування 0
constexpr uint8_t REG_DSP_CTRL1       = 0x2D; // Контролер форматування 1
constexpr uint8_t REG_DSP_ZMOW        = 0x51; // Zoom output width
constexpr uint8_t REG_DSP_ZMOH        = 0x52; // Zoom output height
constexpr uint8_t REG_DSP_ZSOW        = 0x53; // Zoom start output width
constexpr uint8_t REG_DSP_ZSOH        = 0x54; // Zoom start output height

// Базова таблиця ініціалізації для банку Sensor (0x01)
constexpr uint8_t OV2640_SENSOR_INIT[][2] = {
    {REG_BANK_SEL, BANK_SENSOR},
    {REG_SENSOR_CLKRC, 0x01}, // Дільник частоти XCLK
    {REG_SENSOR_COM7,  COM7_RES_SVGA}, // Замовчуваний режим SVGA
    {REG_SENSOR_COM3,  0x38},
    {REG_SENSOR_COM10, 0x00}, // PCLK не інвертований, VSYNC активний High
    {REG_SENSOR_COM8,  0x8F}  // Увімкнено AEC, AGC, AWB
};

// Базова таблиця ініціалізації для банку DSP (0x00)
constexpr uint8_t OV2640_DSP_INIT[][2] = {
    {REG_BANK_SEL, BANK_DSP},
    {REG_DSP_R_BYPASS, 0x00},
    {REG_DSP_CTRL0,    0x0C},
    {REG_DSP_QS,       0x0C}  // Коефіцієнт стиснення JPEG (Quality factor)
};

// Конфігурація для виходу у форматі JPEG SVGA (800x600)
constexpr uint8_t OV2640_JPEG_SVGA_CONFIG[][2] = {
    {REG_BANK_SEL, BANK_SENSOR},
    {REG_SENSOR_COM7, COM7_RES_SVGA},
    {REG_BANK_SEL, BANK_DSP},
    {REG_DSP_ZMOW, 0xA0}, // 800 пікселів по ширині
    {REG_DSP_ZMOH, 0x78}, // 600 пікселів по висоті
    {REG_DSP_QS,   0x0C}  // Середня якість JPEG
};

// Конфігурація для виходу у форматі JPEG UXGA (1600x1200)
constexpr uint8_t OV2640_JPEG_UXGA_CONFIG[][2] = {
    {REG_BANK_SEL, BANK_SENSOR},
    {REG_SENSOR_COM7, COM7_RES_UXGA},
    {REG_BANK_SEL, BANK_DSP},
    {REG_DSP_ZMOW, 0x40}, // 1600 пікселів
    {REG_DSP_ZMOH, 0xF0}, // 1200 пікселів
    {REG_DSP_QS,   0x0F}  // Вища якість для високої роздільності
};

// Конфігурація для виходу у форматі JPEG CIF (352x288)
constexpr uint8_t OV2640_JPEG_CIF_CONFIG[][2] = {
    {REG_BANK_SEL, BANK_SENSOR},
    {REG_SENSOR_COM7, COM7_RES_CIF},
    {REG_BANK_SEL, BANK_DSP},
    {REG_DSP_ZMOW, 0x58}, // 352 пікселі
    {REG_DSP_ZMOH, 0x48}, // 288 пікселів
    {REG_DSP_QS,   0x08}  // Базова якість
};

} // namespace ov2640

#endif // OV2640_REGISTERS_HPP
