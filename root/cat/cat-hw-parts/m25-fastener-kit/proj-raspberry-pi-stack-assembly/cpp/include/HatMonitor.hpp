#pragma once

#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <cstdint>
#include <cstddef>

/**
 * @brief Клас HatMonitor для моніторингу шини I2C та верифікації надійності 
 *        механічного контакту в міжплатному стеку на базі кріплення М2.5.
 * 
 * Реалізує RAII-керування дескриптором файлу шини Linux I2C (/dev/i2c-X).
 */
class HatMonitor {
public:
    /**
     * @brief Конфігурація моніторингу телеметрії HAT.
     */
    struct Config {
        uint8_t status_register = 0x00;  // Регістр стану датчиків
        uint8_t voltage_register = 0x01; // Регістр напруги живлення стека
        uint8_t temp_register = 0x02;    // Регістр температури плати
        size_t retry_count = 3;          // Кількість повторних спроб при збої транзакції
    };

    /**
     * @brief Статистика збоїв та надійності механічного контакту.
     */
    struct Statistics {
        size_t total_queries = 0;   // Загальна кількість спроб опитування
        size_t ack_failures = 0;    // Кількість відмов ACK (поганий контакт / розрив)
        size_t timeouts = 0;        // Кількість тайм-аутів шини
        size_t bus_errors = 0;      // Апаратні помилки шини (брязкіт ліній SDA/SCL)
    };

    /**
     * @brief Конструктор. Відкриває шину I2C та налаштовує адресу веденого пристрою.
     * @param device Шлях до пристрою шини (наприклад, "/dev/i2c-1").
     * @param slave_addr 7-бітна I2C адреса веденого шилда HAT.
     */
    explicit HatMonitor(std::string_view device, uint8_t slave_addr);

    // Заборона копіювання для забезпечення унікальності володіння дескриптором
    HatMonitor(const HatMonitor&) = delete;
    HatMonitor& operator=(const HatMonitor&) = delete;

    // Дозвіл переміщення
    HatMonitor(HatMonitor&& other) noexcept;
    HatMonitor& operator=(HatMonitor&& other) noexcept;

    /**
     * @brief Деструктор. Автоматично закриває дескриптор файлу шини I2C.
     */
    ~HatMonitor();

    /**
     * @brief Перевіряє фізичну наявність веденого пристрою на шині (ACK probe).
     * @return true, якщо пристрій відповідає, false в іншому випадку.
     */
    bool probe();

    /**
     * @brief Читає блок регістрів з апаратного забезпечення HAT.
     * @param reg Початковий регістр для читання.
     * @param length Кількість байтів для читання.
     * @return std::optional з вектором байтів у разі успіху, або std::nullopt при помилці.
     */
    std::optional<std::vector<uint8_t>> readRegister(uint8_t reg, size_t length);

    /**
     * @brief Запускає стрес-тест для детекції брязкоту ліній або перекосів контактів.
     * @param cycles Кількість циклів опитування у стрес-тесті.
     */
    void runStressTest(size_t cycles);

    /**
     * @brief Виводить детальний звіт про якість монтажу стека та статистику відмов.
     */
    void printReport() const;

    /**
     * @brief Повертає зібрану статистику збоїв.
     */
    const Statistics& getStatistics() const noexcept { return stats_; }

private:
    int fd_;                  // Дескриптор файлу шини I2C (-5 якщо не відкрито)
    uint8_t slave_addr_;      // Адреса веденого пристрою
    Config config_;           // Конфігурація регістрів
    Statistics stats_;        // Накопичена статистика збоїв
    bool contact_degraded_;   // Прапорець деградації механічного контакту

    /**
     * @brief Внутрішній метод для ініціалізації зв'язку з драйвером ядра Linux i2c-dev.
     */
    void initBus(std::string_view device);
};
