#include "OledDisplay.hpp"
#include <cstdio>
#include <cstring>
#include <algorithm>

namespace {
// Спрощена 5x7 матриця шрифту ASCII для базових символів (' ', '.', ':', '-', '+', '0'-'9', 'A'-'Z', 'a'-'z')
constexpr uint8_t FONT_5X7[][5] = {
    {0x00, 0x00, 0x00, 0x00, 0x00}, // ' ' (Space)
    {0x00, 0x00, 0x5F, 0x00, 0x00}, // '!'
    {0x00, 0x07, 0x00, 0x07, 0x00}, // '"'
    {0x14, 0x7F, 0x14, 0x7F, 0x14}, // '#'
    {0x24, 0x2A, 0x7F, 0x2A, 0x12}, // '$'
    {0x23, 0x13, 0x08, 0x64, 0x62}, // '%'
    {0x36, 0x49, 0x55, 0x22, 0x50}, // '&'
    {0x00, 0x05, 0x03, 0x00, 0x00}, // '\''
    {0x00, 0x1C, 0x22, 0x41, 0x00}, // '('
    {0x00, 0x41, 0x22, 0x1C, 0x00}, // ')'
    {0x14, 0x08, 0x3E, 0x08, 0x14}, // '*'
    {0x08, 0x08, 0x3E, 0x08, 0x08}, // '+'
    {0x00, 0x50, 0x30, 0x00, 0x00}, // ','
    {0x08, 0x08, 0x08, 0x08, 0x08}, // '-'
    {0x00, 0x60, 0x60, 0x00, 0x00}, // '.'
    {0x20, 0x10, 0x08, 0x04, 0x02}, // '/'
    {0x3E, 0x51, 0x49, 0x45, 0x3E}, // '0'
    {0x00, 0x42, 0x7F, 0x40, 0x00}, // '1'
    {0x42, 0x61, 0x51, 0x49, 0x46}, // '2'
    {0x21, 0x41, 0x45, 0x4B, 0x31}, // '3'
    {0x18, 0x14, 0x12, 0x7F, 0x10}, // '4'
    {0x27, 0x45, 0x45, 0x45, 0x39}, // '5'
    {0x3C, 0x4A, 0x49, 0x49, 0x30}, // '6'
    {0x01, 0x71, 0x09, 0x05, 0x03}, // '7'
    {0x36, 0x49, 0x49, 0x49, 0x36}, // '8'
    {0x06, 0x49, 0x49, 0x29, 0x1E}, // '9'
    {0x00, 0x36, 0x36, 0x00, 0x00}, // ':'
    {0x00, 0x56, 0x36, 0x00, 0x00}, // ';'
    {0x08, 0x14, 0x22, 0x41, 0x00}, // '<'
    {0x14, 0x14, 0x14, 0x14, 0x14}, // '='
    {0x00, 0x41, 0x22, 0x14, 0x08}, // '>'
    {0x02, 0x01, 0x51, 0x09, 0x06}, // '?'
    {0x32, 0x49, 0x79, 0x41, 0x3E}, // '@'
    {0x7E, 0x11, 0x11, 0x11, 0x7E}, // 'A'
    {0x7F, 0x49, 0x49, 0x49, 0x36}, // 'B'
    {0x3E, 0x41, 0x41, 0x41, 0x22}, // 'C'
    {0x7F, 0x41, 0x41, 0x22, 0x1C}, // 'D'
    {0x7F, 0x49, 0x49, 0x49, 0x41}, // 'E'
    {0x7F, 0x09, 0x09, 0x09, 0x01}, // 'F'
    {0x3E, 0x41, 0x49, 0x49, 0x7A}, // 'G'
    {0x7F, 0x08, 0x08, 0x08, 0x7F}, // 'H'
    {0x00, 0x41, 0x7F, 0x41, 0x00}, // 'I'
    {0x20, 0x40, 0x41, 0x3F, 0x01}, // 'J'
    {0x7F, 0x08, 0x14, 0x22, 0x41}, // 'K'
    {0x7F, 0x40, 0x40, 0x40, 0x40}, // 'L'
    {0x7F, 0x02, 0x0C, 0x02, 0x7F}, // 'M'
    {0x7F, 0x04, 0x08, 0x10, 0x7F}, // 'N'
    {0x3E, 0x41, 0x41, 0x41, 0x3E}, // 'O'
    {0x7F, 0x09, 0x09, 0x09, 0x06}, // 'P'
    {0x3E, 0x41, 0x51, 0x21, 0x5E}, // 'Q'
    {0x7F, 0x09, 0x19, 0x29, 0x46}, // 'R'
    {0x46, 0x49, 0x49, 0x49, 0x31}, // 'S'
    {0x01, 0x01, 0x7F, 0x01, 0x01}, // 'T'
    {0x3F, 0x40, 0x40, 0x40, 0x3F}, // 'U'
    {0x1F, 0x20, 0x40, 0x20, 0x1F}, // 'V'
    {0x3F, 0x40, 0x38, 0x40, 0x3F}, // 'W'
    {0x63, 0x14, 0x08, 0x14, 0x63}, // 'X'
    {0x07, 0x08, 0x70, 0x08, 0x07}, // 'Y'
    {0x61, 0x51, 0x49, 0x45, 0x43}  // 'Z'
};
} // namespace

OledDisplay::OledDisplay(II2cBus& bus, uint8_t address)
    : bus_(bus), address_(address) {
    buffer_.fill(0);
}

bool OledDisplay::sendCommand(uint8_t command) {
    uint8_t payload[2] = {0x00, command}; // 0x00 - префікс команди для SSD1306
    return bus_.writeBytes(address_, payload, 2);
}

bool OledDisplay::sendCommandList(const uint8_t* commands, size_t length) {
    for (size_t i = 0; i < length; ++i) {
        if (!sendCommand(commands[i])) {
            return false;
        }
    }
    return true;
}

bool OledDisplay::begin() {
    // Послідовність ініціалізації контролера SSD1306
    constexpr uint8_t initCmds[] = {
        0xAE,       // Display OFF
        0xD5, 0x80, // Set Display Clock Divide Ratio / Oscillator Frequency
        0xA8, 0x3F, // Set Multiplex Ratio (1 to 64 -> 0x3F = 64 lines)
        0xD3, 0x00, // Set Display Offset (0)
        0x40,       // Set Start Line (0)
        0x8D, 0x14, // Enable Charge Pump
        0x20, 0x00, // Memory Addressing Mode (0x00 = Horizontal Addressing Mode)
        0xA1,       // Segment Re-map (A1 = column address 127 is mapped to SEG0)
        0xC8,       // Set COM Output Scan Direction (C8 = remapped mode)
        0xDA, 0x12, // Set COM Pins Hardware Configuration
        0x81, 0xCF, // Set Contrast Control
        0xD9, 0xF1, // Set Pre-charge Period
        0xDB, 0x40, // Set VCOMH Deselect Level
        0xA4,       // Entire Display ON Follow RAM
        0xA6,       // Normal Display (not inverted)
        0xAF        // Display ON
    };

    if (!sendCommandList(initCmds, sizeof(initCmds))) {
        return false;
    }

    clear();
    return update();
}

void OledDisplay::clear() {
    buffer_.fill(0x00);
}

void OledDisplay::drawPixel(uint8_t x, uint8_t y, bool color) {
    if (x >= WIDTH || y >= HEIGHT) {
        return;
    }
    size_t index = x + (y / 8) * WIDTH;
    uint8_t bit = 1 << (y % 8);

    if (color) {
        buffer_[index] |= bit;
    } else {
        buffer_[index] &= ~bit;
    }
}

void OledDisplay::drawString(uint8_t x, uint8_t y, std::string_view text) {
    uint8_t curX = x;
    for (char ch : text) {
        if (curX + 6 > WIDTH) {
            break; // Перевищення межі екрана
        }

        // Перетворення нижнього регістру у верхній для спрощеної таблиці шрифтів
        char c = ch;
        if (c >= 'a' && c <= 'z') {
            c -= ('a' - 'A');
        }

        if (c >= ' ' && c <= 'Z') {
            size_t fontIndex = static_cast<size_t>(c - ' ');
            for (uint8_t col = 0; col < 5; ++col) {
                uint8_t line = FONT_5X7[fontIndex][col];
                for (uint8_t row = 0; row < 7; ++row) {
                    bool pixel = (line & (1 << row)) != 0;
                    drawPixel(curX + col, y + row, pixel);
                }
            }
        }
        curX += 6; // 5 пікселів символ + 1 піксель міжсимвольний інтервал
    }
}

void OledDisplay::displayPowerMetrics(double voltageV, double currentA, double powerW, bool alertActive) {
    clear();

    // Заголовок
    drawString(0, 0, "--- INA226 MONITOR ---");

    // Форматування напруги
    char bufV[32];
    std::snprintf(bufV, sizeof(bufV), "BUS V: %6.3f V", voltageV);
    drawString(0, 16, bufV);

    // Форматування струму
    char bufI[32];
    std::snprintf(bufI, sizeof(bufI), "CURR : %6.3f A", currentA);
    drawString(0, 28, bufI);

    // Форматування потужності
    char bufP[32];
    std::snprintf(bufP, sizeof(bufP), "POWER: %6.3f W", powerW);
    drawString(0, 40, bufP);

    // Статус системи / тривога ALERT
    if (alertActive) {
        drawString(0, 54, "[ALERT! LIMIT EXCEEDED]");
    } else {
        drawString(0, 54, "STATUS: NORMAL");
    }
}

void OledDisplay::displayAlertBanner(std::string_view message) {
    // Рамка для попередження
    for (uint8_t x = 0; x < WIDTH; ++x) {
        drawPixel(x, 48, true);
        drawPixel(x, 63, true);
    }
    drawString(2, 52, message);
}

bool OledDisplay::update() {
    // 1. Встановлення діапазону колонок (0..127) та сторінок (0..7) в режимі Horizontal Addressing Mode
    constexpr uint8_t setRangeCmds[] = {
        0x21, 0, 127, // Set Column Address
        0x22, 0, 7    // Set Page Address
    };
    if (!sendCommandList(setRangeCmds, sizeof(setRangeCmds))) {
        return false;
    }

    // 2. Відправка даних буфера з префіксом 0x40 (Data stream)
    // Розбиваємо відправку на блоки для стабільності на I2C
    constexpr size_t CHUNK_SIZE = 64;
    uint8_t payload[CHUNK_SIZE + 1];
    payload[0] = 0x40; // Data byte prefix

    for (size_t offset = 0; offset < BUFFER_SIZE; offset += CHUNK_SIZE) {
        size_t currentChunk = std::min(CHUNK_SIZE, BUFFER_SIZE - offset);
        std::memcpy(&payload[1], &buffer_[offset], currentChunk);

        if (!bus_.writeBytes(address_, payload, currentChunk + 1)) {
            return false;
        }
    }

    return true;
}
