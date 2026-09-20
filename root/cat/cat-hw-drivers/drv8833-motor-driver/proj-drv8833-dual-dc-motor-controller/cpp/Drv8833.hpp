#ifndef DRV8833_HPP
#define DRV8833_HPP

#include <cstdint>

/**
 * @brief Перелік каналів моторів двоканального драйвера DRV8833
 */
enum class MotorChannel : uint8_t {
    ChannelA = 0, ///< Канал А (керує мотором A через піни AIN1/AIN2)
    ChannelB = 1  ///< Канал B (керує мотором B через піни BIN1/BIN2)
};

/**
 * @brief Перелік режимів роботи H-моста для конкретного мотора
 */
enum class MotorMode : uint8_t {
    Coast = 0, ///< Вільний хід (High-Z / ковзання): IN1 = 0, IN2 = 0
    Forward,   ///< Рух вперед: IN1 = ШІМ, IN2 = 0
    Reverse,   ///< Рух назад: IN1 = 0, IN2 = ШІМ
    Brake      ///< Активне гальмування (коротке замикання обмотки): IN1 = 1, IN2 = 1
};

/**
 * @brief Структура налаштувань пінів та параметрів захисту DRV8833
 */
struct Drv8833Config {
    uint8_t ain1_pin;    ///< Пін керування AIN1 (підтримка ШІМ)
    uint8_t ain2_pin;    ///< Пін керування AIN2 (підтримка ШІМ)
    uint8_t bin1_pin;    ///< Пін керування BIN1 (підтримка ШІМ)
    uint8_t bin2_pin;    ///< Пін керування BIN2 (підтримка ШІМ)
    int8_t  nsleep_pin;  ///< Пін nSLEEP (активний НИЗЬКИЙ, -1 якщо підключено напряму до VCC)
    int8_t  nfault_pin;  ///< Пін nFAULT (відкритий колектор, активний НИЗЬКИЙ, -1 якщо не використовується)
    uint32_t timeout_ms; ///< Таймаут бездіяльності в мс для автозупинки (0 — вимкнено)
};

/**
 * @brief Клас C++ для обгортки та керування двоканальним H-мостом DRV8833
 */
class Drv8833 {
public:
    /**
     * @brief Конструктор класу Drv8833
     * @param config Структура з конфігурацією пінів мікроконтролера та параметрами
     */
    explicit Drv8833(const Drv8833Config& config);

    /**
     * @brief Деструктор класу
     */
    ~Drv8833();

    /**
     * @brief Ініціалізація режимів робочих пінів мікроконтролера
     */
    void begin();

    /**
     * @brief Програмне ввімкнення драйвера (вихід зі стану сну nSLEEP = HIGH)
     */
    void enable();

    /**
     * @brief Переведення драйвера у режим сну зі зниженим енергоспоживанням (nSLEEP = LOW)
     */
    void disable();

    /**
     * @brief Перевірка, чи активовано драйвер (nSLEEP у високому стані)
     * @return true, якщо драйвер у робочому стані
     */
    bool isEnabled() const { return m_enabled; }

    /**
     * @brief Встановлення режиму та швидкості ШІМ для одного з моторів
     * @param channel Канал мотора (ChannelA або ChannelB)
     * @param mode Режим роботи (Forward, Reverse, Brake, Coast)
     * @param speed Швидкість від 0 до 255 (значення ШІМ)
     */
    void setMotor(MotorChannel channel, MotorMode mode, uint8_t speed);

    /**
     * @brief Встановлення швидкості мотора зі знаком (знак визначає напрямок)
     * @param channel Канал мотора (ChannelA або ChannelB)
     * @param speed Швидкість від -255 (назад) до +255 (вперед); 0 означає зупинку
     */
    void setSpeed(MotorChannel channel, int16_t speed);

    /**
     * @brief Зупинка вказаного мотора
     * @param channel Канал мотора
     * @param hardBrake true — активне гальмування (Brake), false — вільний хід (Coast)
     */
    void stopMotor(MotorChannel channel, bool hardBrake = true);

    /**
     * @brief Зупинка обох моторів одночасно
     * @param hardBrake true — активне гальмування (Brake), false — вільний хід (Coast)
     */
    void stopAll(bool hardBrake = true);

    /**
     * @brief Перевірка апаратного сигналу помилки на лінії nFAULT
     * @return true при виявленні перевантаження, струмового замикання чи перегріву
     */
    bool hasFault() const;

    /**
     * @brief Перевірка стану аварійної ситуації драйвера
     * @return true, якщо драйвер заблоковано через помилку
     */
    bool isFaultState() const { return m_faultState; }

    /**
     * @brief Скидання прапорця помилки та відновлення роботи після усунення аварії
     */
    void resetFault();

    /**
     * @brief Обслуговування таймера безпеки та апаратних ліній у головному циклі
     * @param currentTimeMs Поточний системний час у мілісекундах
     */
    void update(uint32_t currentTimeMs);

private:
    /**
     * @brief Внутрішній метод встановлення сигналів H-моста на пінах
     */
    void applyHBridge(uint8_t pin1, uint8_t pin2, MotorMode mode, uint8_t speed);

    Drv8833Config m_config;
    bool m_enabled{false};
    bool m_faultState{false};
    uint32_t m_lastCommandTimeMs{0};

    MotorMode m_modeA{MotorMode::Coast};
    MotorMode m_modeB{MotorMode::Coast};
    uint8_t   m_speedA{0};
    uint8_t   m_speedB{0};
};

#endif // DRV8833_HPP
