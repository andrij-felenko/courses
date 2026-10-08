#ifndef COMPASS_RENDERER_HPP
#define COMPASS_RENDERER_HPP

#include "qmc5883l.hpp"
#include <array>
#include <cstdint>

/// @brief Графічний рендерер циферблата компаса для OLED-дисплея SSD1306 (128x64)
class CompassRenderer {
public:
    static constexpr std::size_t SCREEN_WIDTH  = 128;
    static constexpr std::size_t SCREEN_HEIGHT = 64;
    static constexpr std::size_t BUFFER_SIZE   = (SCREEN_WIDTH * SCREEN_HEIGHT) / 8; // 1024 байти

public:
    /// @brief Конструктор рендерера
    /// @param bus Посилання на шину I2C для виведення кадру на дисплей
    /// @param oledAddr I2C адреса дисплея SSD1306 (за замовчуванням 0x3C)
    explicit CompassRenderer(I2CBus& bus, std::uint8_t oledAddr = 0x3C);

    /// @brief Ініціалізація дисплея SSD1306 через I2C
    /// @return true у разі успішної надсилання ініціалізаційних команд
    bool initDisplay();

    /// @brief Очистити графічний буфер кадру
    void clear();

    /// @brief Сформувати кадр цифрового компаса
    /// @param headingDeg Обчислений азимут у градусах [0, 360°)
    /// @param isCalibrating Прапорець відображення статусу калібрування
    void render(float headingDeg, bool isCalibrating);

    /// @brief Відправити вміст графічного буфера кадру на дисплей через I2C
    /// @return true у разі успішної передачі
    bool updateDisplay();

    /// @brief Малювання пікселя в буфері
    void drawPixel(int x, int y, bool color);

    /// @brief Малювання відрізка лінії за алгоритмом Брезенхема
    void drawLine(int x0, int y0, int x1, int y1, bool color);

    /// @brief Малювання кола за алгоритмом Брезенхема
    void drawCircle(int centerX, int centerY, int radius, bool color);

    /// @brief Малювання символу (шрифт 5x7)
    void drawChar(int x, int y, char ch, bool color);

    /// @brief Малювання текстового рядка
    void drawString(int x, int y, const char* str, bool color);

private:
    I2CBus& m_bus;
    std::uint8_t m_oledAddr;
    std::array<std::uint8_t, BUFFER_SIZE> m_buffer{};

    /// @brief Передача службової команди SSD1306
    bool sendCommand(std::uint8_t cmd);

    /// @brief Отримати назву напрямку світу за азимутом (N, NE, E, SE, S, SW, W, NW)
    const char* getCardinalDirection(float headingDeg) const;
};

#endif // COMPASS_RENDERER_HPP
