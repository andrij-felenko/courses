#pragma once

#include <cstdint>
#include <chrono>

/**
 * @brief Абстрактний апаратний інтерфейс для зчитування паралельної шини GPIO.
 */
class IGpioReader {
public:
    virtual ~IGpioReader() = default;

    /**
     * @brief Зчитує 4-бітну комбінацію з фізичних виводів мікроконтролера.
     * @return 4-бітне число (0x0..0xF).
     */
    [[nodiscard]] virtual uint8_t readPinGroup() const = 0;
};

/**
 * @brief Тип кодування контактних дисків ротаційного DIP-перемикача.
 */
enum class EncodingType {
    DirectBinary,        ///< Прямий двійковий / BCD код
    ComplementaryBinary, ///< Комплементарний (інверсний) двійковий код
    GrayCode             ///< Код Ґрея для запобігання проміжним хибним станам
};

/**
 * @brief Клас драйвера ротаційного кодового DIP-перемикача.
 * Реалізує маскування бітів, програмний дебаунсинг та декодування станів.
 */
class RotaryDipSwitch {
public:
    /**
     * @brief Конструктор драйвера перемикача.
     * @param gpio Посилання на об'єкт апаратної абстракції GPIO.
     * @param encoding Тип кодування перемикача.
     * @param debounce_delay Постійна часу програмного згладжування брязкоту.
     */
    RotaryDipSwitch(const IGpioReader& gpio,
                    EncodingType encoding = EncodingType::DirectBinary,
                    std::chrono::milliseconds debounce_delay = std::chrono::milliseconds(10));

    /**
     * @brief Зчитує миттєве сире значення з урахуванням інверсії кодування.
     */
    [[nodiscard]] uint8_t readRawValue() const;

    /**
     * @brief Повертає відфільтроване (згладжене) 4-бітне значення перемикача.
     * @param current_time Поточний часовий штамп системи.
     */
    uint8_t update(std::chrono::steady_clock::time_point current_time);

    /**
     * @brief Повертає декодований чисельний еквівалент (0..15).
     */
    [[nodiscard]] uint8_t getDecodedValue() const;

    /**
     * @brief Перетворює 4-бітний код Ґрея у чисельне двійкове значення.
     */
    [[nodiscard]] static uint8_t grayToBinary(uint8_t gray);

private:
    const IGpioReader& gpio_;
    EncodingType encoding_;
    std::chrono::milliseconds debounce_delay_;

    uint8_t last_raw_state_{0};
    uint8_t stable_state_{0};
    std::chrono::steady_clock::time_point last_change_time_{};
};
