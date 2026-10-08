#pragma once

#include <cstdint>
#include <vector>
#include <utility>

namespace camera {

// Формати вихідних даних камери OV3640
enum class ImageFormat : uint8_t {
    YUV422 = 0,
    JPEG   = 1
};

// Роздільна здатність матриці OV3640
enum class Resolution : uint8_t {
    QXGA_2048x1536 = 0,
    FHD_1920x1080  = 1,
    VGA_640x480    = 2
};

// Структура для опису регістру камери з вказуванням банку
struct RegisterSetting {
    uint8_t bank;
    uint8_t reg;
    uint8_t val;
};

// Визначення адрес регістрів та констант OV3640
namespace registers {

constexpr uint8_t BANK_0 = 0x00;
constexpr uint8_t BANK_1 = 0x01;
constexpr uint8_t BANK_2 = 0x02;

constexpr uint8_t REG_COM7 = 0x12; // Контрольний регістр 7 (програмне скидання)
constexpr uint8_t REG_COM8 = 0x13; // Керування AEC/AGC/AWB
constexpr uint8_t REG_CLKRC = 0x11; // Тактування внутрішнього генератора

constexpr uint8_t COM7_RESET = 0x80; // Біт програмного скидання
constexpr uint8_t COM8_AEC   = 0x01; // Автоматична експозиція
constexpr uint8_t COM8_AGC   = 0x04; // Автоматичне підсилення
constexpr uint8_t COM8_AWB   = 0x02; // Автоматичний баланс білого

// Таблиця скидання й базової конфігурації матриці OV3640
inline const std::vector<RegisterSetting>& get_init_table() {
    static const std::vector<RegisterSetting> table = {
        {BANK_0, 0x12, 0x80}, // Програмне скидання
        {BANK_0, 0x11, 0x00}, // Конфігурація тактування (Prescaler)
        {BANK_0, 0x13, 0x07}, // Увімкнення AWB, AGC, AEC
        {BANK_1, 0x03, 0x10}, // Налаштування DSP
        {BANK_1, 0x32, 0x36}, // Конфігурація піксельного матричного масиву
    };
    return table;
}

// Конфігураційні регістри для вибору роздільності
inline const std::vector<RegisterSetting>& get_resolution_table(Resolution res) {
    static const std::vector<RegisterSetting> qxga_table = {
        {BANK_1, 0x17, 0x00}, {BANK_1, 0x18, 0x80}, // X/Y Window Start
        {BANK_1, 0x19, 0x08}, {BANK_1, 0x1A, 0x00}  // X/Y Window End (2048x1536)
    };
    static const std::vector<RegisterSetting> fhd_table = {
        {BANK_1, 0x17, 0x01}, {BANK_1, 0x18, 0x40},
        {BANK_1, 0x19, 0x07}, {BANK_1, 0x1A, 0x80}  // 1920x1080
    };
    static const std::vector<RegisterSetting> vga_table = {
        {BANK_1, 0x17, 0x02}, {BANK_1, 0x18, 0x10},
        {BANK_1, 0x19, 0x02}, {BANK_1, 0x1A, 0x80}  // 640x480
    };

    switch (res) {
        case Resolution::QXGA_2048x1536: return qxga_table;
        case Resolution::FHD_1920x1080:  return fhd_table;
        case Resolution::VGA_640x480:    return vga_table;
    }
    return vga_table;
}

// Конфігурація форматів виходу YUV422 / JPEG
inline const std::vector<RegisterSetting>& get_format_table(ImageFormat fmt) {
    static const std::vector<RegisterSetting> yuv_table = {
        {BANK_0, 0x12, 0x00}, // Вихід YUV422
        {BANK_2, 0x01, 0x08}  // Обійти модуль JPEG компресії
    };
    static const std::vector<RegisterSetting> jpeg_table = {
        {BANK_0, 0x12, 0x10}, // Увімкнути режим стиснення JPEG
        {BANK_2, 0x01, 0x38}  // Активація внутрішнього кодера JPEG
    };

    return (fmt == ImageFormat::JPEG) ? jpeg_table : yuv_table;
}

} // namespace registers
} // namespace camera
