#ifndef DIP_CONFIGURATOR_HPP
#define DIP_CONFIGURATOR_HPP

#include <cstdint>
#include <array>

/**
 * @brief Перелічення підтримуваних швидкостей обміну (Baudrate)
 */
enum class BaudRate : uint32_t {
    Baud9600 = 9600,
    Baud115200 = 115200,
    Baud250000 = 250000,
    Baud1000000 = 1000000
};

/**
 * @brief Результат розбору конфігурації з DIP-перемикачів
 */
struct ConfigResult {
    uint8_t device_id{0};          ///< Отриманий апаратний ID пристрою (біти 0..1)
    BaudRate baud_rate{BaudRate::Baud115200}; ///< Отримана швидкість I2C/UART (біт 2)
    bool debug_mode{false};        ///< Прапорець режиму відлагодження (біт 3)
    bool is_valid{true};           ///< Ознака коректності конфігурації
    uint8_t raw_mask{0};           ///< Сира побітова маска станів пінів
};

/**
 * @brief Клас для ініціалізації та обробки 4-позиційного DIP-перемикача
 */
class DipConfigurator {
public:
    static constexpr size_t NUM_PINS = 4;

    /**
     * @brief Конструктор конфігуратора
     * @param pin_map Масив номерів GPIO-виводів [BIT0, BIT1, BIT2, BIT3]
     */
    explicit DipConfigurator(const std::array<uint8_t, NUM_PINS>& pin_map);

    /**
     * @brief Ініціалізація GPIO-пінів у режим входу з підтяжкою PULLUP
     */
    void init();

    /**
     * @brief Зчитування побітової маски зі станів перемикачів
     * @return 8-бітна маска (біти 0..3)
     */
    uint8_t readRawMask() const;

    /**
     * @brief Перевірка валідності маски за таблицею заборонених комбінацій
     * @param raw_mask Зчитана побітова маска
     * @return true якщо комбінація дозволена
     */
    bool validateConfig(uint8_t raw_mask) const;

    /**
     * @brief Повний цикл зчитування, перевірки та депонування параметрів із фолбеком
     * @return Заповнена структура ConfigResult
     */
    ConfigResult readAndValidate() const;

private:
    std::array<uint8_t, NUM_PINS> pins_;

    /**
     * @brief Зчитування стану окремого фізичного піна
     */
    bool readPinState(uint8_t pin) const;
};

#endif // DIP_CONFIGURATOR_HPP
