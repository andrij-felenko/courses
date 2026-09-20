#ifndef DIP_CONFIG_HPP
#define DIP_CONFIG_HPP

#include <cstdint>

/**
 * @brief Перелічуваний тип для швидкості обміну даними (біти 3..4).
 */
enum class BaudRate : uint8_t {
    Baud9600   = 0, // 0b00
    Baud19200  = 1, // 0b01
    Baud57600  = 2, // 0b10
    Baud115200 = 3  // 0b11
};

/**
 * @brief Перелічуваний тип для режимів роботи пристрою (біти 5..6).
 */
enum class OperatingMode : uint8_t {
    Normal      = 0, // 0b00 — стандартний робочий режим
    Diagnostic  = 1, // 0b01 — діагностика та сервіс
    Calibration = 2, // 0b10 — режим калібрування сенсорів
    Reserved    = 3  // 0b11 — зарезервований (недопустимий) стан
};

/**
 * @brief Структура збереження розпарсених сильнотипізованих налаштувань.
 */
struct ConfigSettings {
    uint8_t deviceAddress;  ///< Апаратна адреса пристрою (0..7, біти 0..2)
    BaudRate baudRate;      ///< Швидкість послідовного порту (біти 3..4)
    OperatingMode mode;     ///< Режим функціонування (біти 5..6)
    bool parityValid;       ///< Прапорець цілісності даних (бітова парність)
};

/**
 * @brief Клас для декодування та валідації сирого конфігураційного байта DIP-перемикачів.
 *
 * Бітова карта конфігураційного байта (8 бітів):
 * [7]   : Біт парності (Parity Bit)
 * [6:5] : Режим роботи (Operating Mode)
 * [4:3] : Швидкість шини (Baud Rate)
 * [2:0] : Апаратна адреса (Device Address: 0..7)
 */
class DipConfig {
public:
    // Побітові маски та зсуви для витягнення полів
    static constexpr uint8_t MASK_ADDRESS = 0x07; // 0b00000111 (біти 0..2)
    static constexpr uint8_t MASK_BAUD    = 0x18; // 0b00011000 (біти 3..4)
    static constexpr uint8_t MASK_MODE    = 0x60; // 0b01100000 (біти 5..6)
    static constexpr uint8_t MASK_PARITY  = 0x80; // 0b10000000 (біт 7)

    static constexpr uint8_t SHIFT_BAUD   = 3;
    static constexpr uint8_t SHIFT_MODE   = 5;
    static constexpr uint8_t SHIFT_PARITY = 7;

    /**
     * @brief Конструктор прийняття сирого конфігураційного байта.
     * @param rawByte Байт, зчитаний з DIP-перемикачів або зсувного регістра.
     */
    explicit DipConfig(uint8_t rawByte);

    /**
     * @brief Повертає початковий сирий байт.
     */
    uint8_t getRawByte() const;

    /**
     * @brief Витягує апаратну адресу (біти 0..2).
     */
    uint8_t getDeviceAddress() const;

    /**
     * @brief Витягує та типізує швидкість обміну даними (біти 3..4).
     */
    BaudRate getBaudRate() const;

    /**
     * @brief Витягує та типізує режим роботи (біти 5..6).
     */
    OperatingMode getOperatingMode() const;

    /**
     * @brief Обчислює контрольний біт парності для інформаційних бітів [0..6].
     * @return true якщо кількість одиничних бітів непарна, false якщо парна.
     */
    bool calculateParity() const;

    /**
     * @brief Перевіряє збіг обчисленої парності з отриманим бітом P_recv [7].
     */
    bool isParityValid() const;

    /**
     * @brief Декодує конфігурацію у структуру з перевіркою цілісності.
     * @param outSettings Вихідна структура із розпарсеними значеннями.
     * @return true якщо конфігурація валідна (парність OK та режим != Reserved).
     */
    bool parse(ConfigSettings& outSettings) const;

private:
    uint8_t m_rawByte;
};

#endif // DIP_CONFIG_HPP
