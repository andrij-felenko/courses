#ifndef THUMBWHEEL_74HC165_HPP
#define THUMBWHEEL_74HC165_HPP

#include <cstdint>
#include <cstddef>
#include <array>
#include <functional>

/**
 * @brief Статус виконання операцій драйвера декадних перемикачів.
 */
enum class ThumbwheelStatus : int8_t {
    Ok                  =  0,  ///< Успішна операція / валідні BCD-дані
    ErrInvalidBcd       = -1,  ///< Виявлено невалідну BCD-тетраду (10...15)
    ErrInvalidConfig    = -2   ///< Некоректна конфігурація (наприклад, 0 декад)
};

/**
 * @brief Абстрактний інтерфейс для GPIO-операцій мікроконтролера.
 */
struct GpioPin {
    uint8_t pinNumber{0};
    std::function<void(bool level)> write;
    std::function<bool()> read;
    std::function<void(uint32_t ns)> delayNs;
};

/**
 * @brief Апаратна конфігурація зсувних регістрів 74HC165 та декадного масиву.
 */
struct ThumbwheelConfig {
    GpioPin pinPl;             ///< Пін паралельного завантаження (Parallel Load, активний низький)
    GpioPin pinClk;            ///< Пін тактування (Clock)
    GpioPin pinData;           ///< Пін послідовних даних Q7 (Serial Data In)
    uint8_t decadesCount{4};   ///< Кількість 4-бітних декадних барабанів (макс. 4)
    bool activeLowLogic{true}; ///< true, якщо замкнений контакт дає низький рівень GND (з підтяжкою до VCC)
    uint8_t debounceThreshold{3}; ///< Кількість послідовних однакових замірів для підтвердження
};

/**
 * @brief Клас драйвера зчитування, фільтрації та валідації BCD-перемикачів на 74HC165.
 */
class Thumbwheel74HC165 {
public:
    using ChangeCallback = std::function<void(uint16_t newValue, uint16_t oldValue)>;

    Thumbwheel74HC165() = default;

    /**
     * @brief Ініціалізація периферії та налаштування драйвера.
     */
    ThumbwheelStatus init(const ThumbwheelConfig& config);

    /**
     * @brief Циклічний крок опитування регістрів, фільтрації та валідації.
     * @return ThumbwheelStatus::Ok при валідному зчитуванні, або код помилки.
     */
    ThumbwheelStatus poll();

    /**
     * @brief Отримання поточного підтвердженого цілочисельного значення (наприклад, 0...9999).
     */
    [[nodiscard]] uint16_t getValue() const noexcept { return validatedValue_; }

    /**
     * @brief Отримання відфільтрованої BCD-тетради конкретної декади (0...decadesCount-1).
     */
    [[nodiscard]] uint8_t getNibble(uint8_t index) const noexcept;

    /**
     * @brief Встановлення зворотного виклику (callback) на зміну валідованої устави.
     */
    void setOnChangeCallback(ChangeCallback cb) { onChangeCb_ = std::move(cb); }

private:
    uint16_t readRawShiftRegister();
    bool parseAndValidateNibbles(uint16_t rawFrame, std::array<uint8_t, 4>& outNibbles);
    void applyDebounceFilter(const std::array<uint8_t, 4>& currentNibbles);

    ThumbwheelConfig config_{};
    bool isInitialized_{false};
    uint16_t rawLatch_{0};
    uint16_t validatedValue_{0};

    std::array<uint8_t, 4> filteredNibbles_{0, 0, 0, 0};
    std::array<uint8_t, 4> candidateNibbles_{0, 0, 0, 0};
    std::array<uint8_t, 4> debounceCounters_{0, 0, 0, 0};

    ChangeCallback onChangeCb_{nullptr};
};

#endif // THUMBWHEEL_74HC165_HPP
