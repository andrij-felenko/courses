#include "compass_renderer.hpp"
#include <cmath>
#include <cstdio>
#include <cstring>

namespace {
    constexpr float PI_F = 3.14159265358979323846f;

    // Вбудована матриця шрифту ASCII 5x7 для цифр, літер та символів
    const std::uint8_t FONT_5X7[][5] = {
        {0x3E, 0x51, 0x49, 0x45, 0x3E}, // '0' (index 0)
        {0x00, 0x42, 0x7F, 0x40, 0x00}, // '1'
        {0x42, 0x61, 0x51, 0x49, 0x46}, // '2'
        {0x21, 0x41, 0x45, 0x4B, 0x31}, // '3'
        {0x18, 0x14, 0x12, 0x7F, 0x10}, // '4'
        {0x27, 0x45, 0x45, 0x45, 0x39}, // '5'
        {0x3C, 0x4A, 0x49, 0x49, 0x30}, // '6'
        {0x01, 0x71, 0x09, 0x05, 0x03}, // '7'
        {0x36, 0x49, 0x49, 0x49, 0x36}, // '8'
        {0x06, 0x49, 0x49, 0x29, 0x1E}, // '9'
        {0x7F, 0x08, 0x08, 0x08, 0x7F}, // 'H' (index 10)
        {0x7F, 0x09, 0x19, 0x29, 0x46}, // 'R'
        {0x3E, 0x41, 0x41, 0x41, 0x22}, // 'C'
        {0x7C, 0x12, 0x11, 0x12, 0x7C}, // 'A'
        {0x7F, 0x40, 0x40, 0x40, 0x40}, // 'L'
        {0x7F, 0x02, 0x0C, 0x02, 0x7F}, // 'M'
        {0x7F, 0x04, 0x08, 0x10, 0x7F}, // 'N' (index 16)
        {0x7F, 0x49, 0x49, 0x49, 0x41}, // 'E'
        {0x46, 0x49, 0x49, 0x49, 0x31}, // 'S'
        {0x3F, 0x40, 0x38, 0x40, 0x3F}, // 'W'
        {0x00, 0x00, 0x60, 0x60, 0x00}, // '.' (index 20)
        {0x00, 0x00, 0x00, 0x00, 0x00}, // ' ' (space)
        {0x00, 0x06, 0x09, 0x09, 0x06}, // ° (degree symbol)
        {0x00, 0x36, 0x36, 0x00, 0x00}  // ':'
    };

    const std::uint8_t* getFontColumn(char c) {
        if (c >= '0' && c <= '9') return FONT_5X7[c - '0'];
        switch (c) {
            case 'H': return FONT_5X7[10];
            case 'R': return FONT_5X7[11];
            case 'C': return FONT_5X7[12];
            case 'A': return FONT_5X7[13];
            case 'L': return FONT_5X7[14];
            case 'M': return FONT_5X7[15];
            case 'N': return FONT_5X7[16];
            case 'E': return FONT_5X7[17];
            case 'S': return FONT_5X7[18];
            case 'W': return FONT_5X7[19];
            case '.': return FONT_5X7[20];
            case ' ': return FONT_5X7[21];
            case '*': return FONT_5X7[22];
            case ':': return FONT_5X7[23];
            default:  return FONT_5X7[21];
        }
    }
}

CompassRenderer::CompassRenderer(I2CBus& bus, std::uint8_t oledAddr)
    : m_bus(bus), m_oledAddr(oledAddr) {
    m_buffer.fill(0x00);
}

bool CompassRenderer::sendCommand(std::uint8_t cmd) {
    // В протоколі SSD1306 байт 0x00 означає передачу команди
    return m_bus.writeRegister(m_oledAddr, 0x00, cmd);
}

bool CompassRenderer::initDisplay() {
    // Стандартна послідовність ініціалізації OLED SSD1306 (128x64)
    static const std::uint8_t initCmds[] = {
        0xAE,       // Display OFF
        0xD5, 0x80, // Set Display Clock Divide Ratio
        0xA8, 0x3F, // Set Multiplex Ratio (64 lines)
        0xD3, 0x00, // Display Offset = 0
        0x40,       // Start Line = 0
        0x8D, 0x14, // Enable Charge Pump
        0x20, 0x00, // Memory Addressing Mode = Horizontal
        0xA1,       // Segment Re-map (A0/A1)
        0xC8,       // COM Output Scan Direction
        0xDA, 0x12, // Set COM Pins Hardware Configuration
        0x81, 0xCF, // Set Contrast Control
        0xD9, 0xF1, // Set Pre-charge Period
        0xDB, 0x40, // Set VCOMH Deselect Level
        0xA4,       // Entire Display ON (Resume to RAM content)
        0xA6,       // Normal Display (Not Inverted)
        0xAF        // Display ON
    };

    for (std::uint8_t cmd : initCmds) {
        if (!sendCommand(cmd)) {
            return false;
        }
    }
    clear();
    return updateDisplay();
}

void CompassRenderer::clear() {
    m_buffer.fill(0x00);
}

void CompassRenderer::drawPixel(int x, int y, bool color) {
    if (x < 0 || x >= static_cast<int>(SCREEN_WIDTH) || y < 0 || y >= static_cast<int>(SCREEN_HEIGHT)) {
        return;
    }
    std::size_t index = static_cast<std::size_t>(x) + static_cast<std::size_t>(y / 8) * SCREEN_WIDTH;
    std::uint8_t bitMask = 1 << (y % 8);

    if (color) {
        m_buffer[index] |= bitMask;
    } else {
        m_buffer[index] &= ~bitMask;
    }
}

void CompassRenderer::drawLine(int x0, int y0, int x1, int y1, bool color) {
    int dx = std::abs(x1 - x0);
    int dy = std::abs(y1 - y0);
    int sx = (x0 < x1) ? 1 : -1;
    int sy = (y0 < y1) ? 1 : -1;
    int err = dx - dy;

    while (true) {
        drawPixel(x0, y0, color);
        if (x0 == x1 && y0 == y1) break;
        int e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            x0 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y0 += sy;
        }
    }
}

void CompassRenderer::drawCircle(int centerX, int centerY, int radius, bool color) {
    int x = radius;
    int y = 0;
    int err = 0;

    while (x >= y) {
        drawPixel(centerX + x, centerY + y, color);
        drawPixel(centerX + y, centerY + x, color);
        drawPixel(centerX - y, centerY + x, color);
        drawPixel(centerX - x, centerY + y, color);
        drawPixel(centerX - x, centerY - y, color);
        drawPixel(centerX - y, centerY - x, color);
        drawPixel(centerX + y, centerY - x, color);
        drawPixel(centerX + x, centerY - y, color);

        if (err <= 0) {
            y += 1;
            err += 2 * y + 1;
        }
        if (err > 0) {
            x -= 1;
            err -= 2 * x + 1;
        }
    }
}

void CompassRenderer::drawChar(int x, int y, char ch, bool color) {
    const std::uint8_t* cols = getFontColumn(ch);
    for (int i = 0; i < 5; ++i) {
        std::uint8_t line = cols[i];
        for (int j = 0; j < 7; ++j) {
            if (line & (1 << j)) {
                drawPixel(x + i, y + j, color);
            }
        }
    }
}

void CompassRenderer::drawString(int x, int y, const char* str, bool color) {
    while (*str) {
        drawChar(x, y, *str, color);
        x += 6; // 5 пікселів символ + 1 піксель міжсимвольний інтервал
        str++;
    }
}

const char* CompassRenderer::getCardinalDirection(float headingDeg) const {
    if (headingDeg >= 337.5f || headingDeg < 22.5f)  return "N";
    if (headingDeg >= 22.5f  && headingDeg < 67.5f)  return "NE";
    if (headingDeg >= 67.5f  && headingDeg < 112.5f) return "E";
    if (headingDeg >= 112.5f && headingDeg < 157.5f) return "SE";
    if (headingDeg >= 157.5f && headingDeg < 202.5f) return "S";
    if (headingDeg >= 202.5f && headingDeg < 247.5f) return "SW";
    if (headingDeg >= 247.5f && headingDeg < 292.5f) return "W";
    if (headingDeg >= 292.5f && headingDeg < 337.5f) return "NW";
    return "N";
}

void CompassRenderer::render(float headingDeg, bool isCalibrating) {
    clear();

    // Центр та радіус циферблата компаса на лівій половині екрана
    const int centerX = 32;
    const int centerY = 32;
    const int radius  = 26;

    // 1. Малювання зовнішнього кола компаса
    drawCircle(centerX, centerY, radius, true);
    drawCircle(centerX, centerY, 1, true); // Центральна точка

    // 2. Відрисовування позначок румбів (N, E, S, W)
    drawChar(centerX - 2, centerY - radius + 2, 'N', true);
    drawChar(centerX + radius - 6, centerY - 3, 'E', true);
    drawChar(centerX - 2, centerY + radius - 8, 'S', true);
    drawChar(centerX - radius + 2, centerY - 3, 'W', true);

    // 3. Тригонометричний розрахунок орієнтації динамічної вказівної стрілки
    // Вершина стрілки вказує на Північ відносно орієнтації корпусу
    // Кут 0° відповідає напрямку вгору (-Y в екранній системі координат)
    float needleRad = (headingDeg - 90.0f) * (PI_F / 180.0f);
    int tipX = centerX + static_cast<int>(std::round(std::cos(needleRad) * (radius - 5)));
    int tipY = centerY + static_cast<int>(std::round(std::sin(needleRad) * (radius - 5)));

    // Малювання лінії стрілки компаса від центру до вказівника
    drawLine(centerX, centerY, tipX, tipY, true);

    // Малювання стрілки з покажчиком у формі трикутника
    float leftRad = (headingDeg - 90.0f + 150.0f) * (PI_F / 180.0f);
    float rightRad = (headingDeg - 90.0f - 150.0f) * (PI_F / 180.0f);
    int leftX = tipX + static_cast<int>(std::round(std::cos(leftRad) * 6.0f));
    int leftY = tipY + static_cast<int>(std::round(std::sin(leftRad) * 6.0f));
    int rightX = tipX + static_cast<int>(std::round(std::cos(rightRad) * 6.0f));
    int rightY = tipY + static_cast<int>(std::round(std::sin(rightRad) * 6.0f));

    drawLine(tipX, tipY, leftX, leftY, true);
    drawLine(tipX, tipY, rightX, rightY, true);
    drawLine(leftX, leftY, rightX, rightY, true);

    // 4. Текстовий рендеринг у правій секції екрана (X = 64..127)
    drawString(68, 4, "COMPASS", true);

    char valBuf[16];
    std::snprintf(valBuf, sizeof(valBuf), "%3.1f*", headingDeg);
    drawString(68, 20, valBuf, true);

    const char* dirStr = getCardinalDirection(headingDeg);
    drawString(68, 34, dirStr, true);

    if (isCalibrating) {
        drawString(68, 50, "CAL...", true);
    } else {
        drawString(68, 50, "READY", true);
    }
}

bool CompassRenderer::updateDisplay() {
    // Встановлюємо діапазони колонок та сторінок SSD1306
    if (!sendCommand(0x21)) return false; // Column addr
    if (!sendCommand(0x00)) return false; // Start 0
    if (!sendCommand(127))  return false; // End 127

    if (!sendCommand(0x22)) return false; // Page addr
    if (!sendCommand(0x00)) return false; // Start 0
    if (!sendCommand(7))    return false; // End 7

    // Передаємо 1024 байти кадрів блоками через I2C
    // У SSD1306 байт 0x40 вказує, що наступні байти — це дані графічного RAM
    for (std::size_t i = 0; i < BUFFER_SIZE; ++i) {
        if (!m_bus.writeRegister(m_oledAddr, 0x40, m_buffer[i])) {
            return false;
        }
    }
    return true;
}
