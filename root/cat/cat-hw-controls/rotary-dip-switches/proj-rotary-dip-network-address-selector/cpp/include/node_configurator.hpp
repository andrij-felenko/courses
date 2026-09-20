#pragma once

#include "rotary_dip_switch.hpp"
#include <cstdint>

/**
 * @brief Перелічування підтримуваних швидкостей обміну даних мережевої шини.
 */
enum class Baudrate : uint32_t {
    Baud125k  = 125000,
    Baud250k  = 250000,
    Baud500k  = 500000,
    Baud1000k = 1000000
};

/**
 * @brief Структура результату обчислення мережевої конфігурації вузла.
 */
struct NodeConfiguration {
    uint8_t node_id{0};             ///< Обчислений Node ID (1..127 для CANopen/Modbus)
    Baudrate baudrate{Baudrate::Baud125k}; ///< Швидкість обміну даних
    bool is_valid{false};           ///< Прапорець коректності параметрів
};

/**
 * @brief Клас конфігуратора мережевого вузла.
 * Агрегує дані з кількох ротаційних перемикачів для формування адреси та Baudrate.
 */
class NodeConfigurator {
public:
    /**
     * @brief Конструктор конфігуратора.
     * @param sw_high Перемикач старшого ніблу адреси (High / Tens).
     * @param sw_low Перемикач молодшого ніблу адреси (Low / Units).
     * @param sw_baud Перемикач вибору швидкості Baudrate.
     */
    NodeConfigurator(RotaryDipSwitch& sw_high,
                     RotaryDipSwitch& sw_low,
                     RotaryDipSwitch& sw_baud);

    /**
     * @brief Опитує всі перемикачі та обчислює підсумкову мережеву конфігурацію.
     * @param now Поточний момент часу для оновлення дебаунсингу.
     */
    NodeConfiguration evaluateConfiguration(std::chrono::steady_clock::time_point now);

    /**
     * @brief Декодує позицію перемикача швидкості у значення Baudrate.
     */
    [[nodiscard]] static Baudrate parseBaudrate(uint8_t position);

private:
    RotaryDipSwitch& sw_high_;
    RotaryDipSwitch& sw_low_;
    RotaryDipSwitch& sw_baud_;
};
