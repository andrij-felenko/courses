#pragma once

#include <Arduino.h>

// Конфігурація підключення та параметрів кадру абсолютного енкодера
struct EncoderConfig {
    uint8_t clkPin;          // Пін генерації тактового сигналу (CLK / MA)
    uint8_t dataPin;         // Пін зчитування послідовних даних (DATA / SLO)
    uint8_t singleTurnBits;  // Кількість бітів однооборотного кута (наприклад, 13 біт)
    uint8_t multiTurnBits;   // Кількість бітів багатооборотного лічильника (наприклад, 12 біт)
    uint16_t clockPeriodUs;  // Період тактування шини в мікросекундах
    bool useGrayCode;        // Чи використовується код Грея для кодування позиції
};

// Результат зчитування та розбору кадру енкодера
struct EncoderFrame {
    uint32_t singleTurnPosition{0}; // Двійкова кутова позиція в межах одного обороту
    uint32_t multiTurnCount{0};     // Лічильник повних оборотів вала
    bool statusWarn{false};         // Прапорець попередження енкодера (Warning)
    bool statusErr{false};          // Прапорець апаратної помилки енкодера (Error)
    bool crcValid{false};           // Результат перевірки цілісності кадру CRC-6
    bool valid{false};              // Загальний прапор валідності кадру
};

class AbsoluteEncoder {
public:
    explicit AbsoluteEncoder(const EncoderConfig& config);
    ~AbsoluteEncoder();

    // Ініціалізація GPIO-пінів
    void begin();

    // Опитування енкодера та зчитання кадру
    EncoderFrame readFrame();

    // Перетворення коду Грея у двійковий формат
    static uint32_t grayToBinary(uint32_t gray);

    // Обчислення контрольної суми CRC-6
    static uint8_t calculateCRC6(uint64_t data, uint8_t bitLength);

private:
    EncoderConfig m_config;
};
