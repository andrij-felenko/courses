#pragma once

#include "Ina226.hpp"
#include <cstdint>
#include <cstddef>
#include <array>
#include <string_view>

// Клас для відображення даних моніторингу живлення на OLED-дисплеї SSD1306 (128x64) по I2C
class OledDisplay {
public:
    static constexpr uint8_t WIDTH = 128;
    static constexpr uint8_t HEIGHT = 64;
    static constexpr size_t BUFFER_SIZE = (WIDTH * HEIGHT) / 8; // 1024 байти

    explicit OledDisplay(II2cBus& bus, uint8_t address = 0x3C);

    // Ініціалізація дисплея SSD1306
    bool begin();

    // Очищення графічного буфера
    void clear();

    // Встановлення окремого пікселя у буфері
    void drawPixel(uint8_t x, uint8_t y, bool color = true);

    // Виведення текстового рядка за координатами (x, y)
    void drawString(uint8_t x, uint8_t y, std::string_view text);

    // Спеціалізоване малювання текстових полів монітора живлення
    void displayPowerMetrics(double voltageV, double currentA, double powerW, bool alertActive = false);

    // Виведення повідомлення про порогову подію/аварію
    void displayAlertBanner(std::string_view message);

    // Відправка фреймбуфера на екран по шині I2C
    bool update();

private:
    II2cBus& bus_;
    uint8_t address_;
    std::array<uint8_t, BUFFER_SIZE> buffer_{};

    // Допоміжні методи для відправки команд та даних SSD1306
    bool sendCommand(uint8_t command);
    bool sendCommandList(const uint8_t* commands, size_t length);
};
