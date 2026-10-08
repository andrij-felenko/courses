#ifndef QMC5883L_HPP
#define QMC5883L_HPP

#include <cstdint>
#include <cstddef>
#include <array>
#include <cmath>

// ============================================================================
// Допоміжні структури даних
// ============================================================================

/// @brief Тривимірний вектор магнітного поля або вимірювань
struct Vector3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    Vector3D operator+(const Vector3D& other) const {
        return {x + other.x, y + other.y, z + other.z};
    }

    Vector3D operator-(const Vector3D& other) const {
        return {x - other.x, y - other.y, z - other.z};
    }

    Vector3D operator*(float scalar) const {
        return {x * scalar, y * scalar, z * scalar};
    }

    /// @brief Обчислення довжини (норми) вектора
    float length() const {
        return std::sqrt(x * x + y * y + z * z);
    }
};

/// @brief Сирі 16-бітні знакові значення по трьох осях
struct RawVector3D {
    std::int16_t x{0};
    std::int16_t y{0};
    std::int16_t z{0};
};

// ============================================================================
// Інтерфейс для апаратної шини I2C (Hardware Abstraction Layer)
// ============================================================================

/// @brief Абстрактний інтерфейс шини I2C для забезпечення переносності драйвера
class I2CBus {
public:
    virtual ~I2CBus() = default;

    /// @brief Запис одного байта у вказаний регістр пристрою
    virtual bool writeRegister(std::uint8_t devAddr, std::uint8_t regAddr, std::uint8_t data) = 0;

    /// @brief Зчитати один байт із вказаного регістра
    virtual bool readRegister(std::uint8_t devAddr, std::uint8_t regAddr, std::uint8_t& data) = 0;

    /// @brief Зчитати послідовний блок байтів починаючи з regAddr
    virtual bool readBytes(std::uint8_t devAddr, std::uint8_t regAddr, std::uint8_t* buffer, std::size_t length) = 0;
};

// ============================================================================
// Клас драйвера магнітометра QMC5883L
// ============================================================================

class QMC5883L {
public:
    /// @brief Адреса I2C за замовчуванням для QMC5883L
    static constexpr std::uint8_t DEFAULT_I2C_ADDR = 0x0D;

    /// @brief Адреси внутрішніх регістрів QMC5883L
    enum class Register : std::uint8_t {
        OUT_X_L    = 0x00,
        OUT_X_H    = 0x01,
        OUT_Y_L    = 0x02,
        OUT_Y_H    = 0x03,
        OUT_Z_L    = 0x04,
        OUT_Z_H    = 0x05,
        STATUS     = 0x06,
        TEMP_L     = 0x07,
        TEMP_H     = 0x08,
        CONTROL_1  = 0x09,
        CONTROL_2  = 0x0A,
        SET_RESET  = 0x0B
    };

    /// @brief Режим роботи сенсора (Mode)
    enum class Mode : std::uint8_t {
        Standby    = 0x00, // Режим очікування з мінімальним енергоспоживанням
        Continuous = 0x01  // Безперервний режим вимірювання
    };

    /// @brief Частота виходу даних (Output Data Rate - ODR)
    enum class ODR : std::uint8_t {
        Hz10  = 0x00 << 2, // 10 Гц
        Hz50  = 0x01 << 2, // 50 Гц
        Hz100 = 0x02 << 2, // 100 Гц
        Hz200 = 0x03 << 2  // 200 Гц
    };

    /// @brief Шкала вимірювання (Full Scale Range - RNG)
    enum class Range : std::uint8_t {
        G2 = 0x00 << 4, // ±2 Гаус (12000 LSB/G)
        G8 = 0x01 << 4  // ±8 Гаус (3000 LSB/G)
    };

    /// @brief Коефіцієнт передискретизації (Over Sampling Ratio - OSR)
    enum class OSR : std::uint8_t {
        OSR512 = 0x00 << 6, // 512 відліків (найвища точність)
        OSR256 = 0x01 << 6, // 256 відліків
        OSR128 = 0x02 << 6, // 128 відліків
        OSR64  = 0x03 << 6  // 64 відліки (найменша затримка)
    };

    /// @brief Біти прапорців регістру стану (STATUS 0x06)
    struct StatusFlags {
        bool dataReady;  // DRDY: дані готові для зчитування
        bool overflow;   // OVL: переповнення діапазону вимірювання
        bool dataSkip;   // DOR: пропуск зчитування попереднього відліку
    };

public:
    /// @brief Конструктор драйвера
    /// @param bus Посилання на об'єкт апаратної шини I2C
    /// @param address Адреса пристрою на шині I2C (за замовчуванням 0x0D)
    explicit QMC5883L(I2CBus& bus, std::uint8_t address = DEFAULT_I2C_ADDR);

    /// @brief Ініціалізація та конфігурація регістрів сенсора
    /// @param mode Режим роботи (Continuous / Standby)
    /// @param odr Частота оновлення даних
    /// @param range Діапазон вимірювання (2G або 8G)
    /// @param osr Коефіцієнт усреднення/передискретизації
    /// @return true у разі успішної конфігурації
    bool begin(Mode mode = Mode::Continuous,
               ODR odr = ODR::Hz200,
               Range range = Range::G8,
               OSR osr = OSR::OSR512);

    /// @brief Виконати програмове скидання сенсора (Soft Reset)
    /// @return true якщо команду успішно передано
    bool softReset();

    /// @brief Отримати поточний стан прапорців готовності та переповнення
    /// @param flags Вихідна структура для запису прапорців
    /// @return true у разі успішного зчитування регістру стану
    bool getStatus(StatusFlags& flags);

    /// @brief Перевірка наявності нових готових вимірів
    /// @return true якщо нові дані готові до зчитування
    bool isDataReady();

    /// @brief Зчитати сирі 16-бітні векторні виміри осей X, Y, Z
    /// @param raw Вихідна структура з цілочисельними відліками
    /// @return true у разі успішного зчитування
    bool readRaw(RawVector3D& raw);

    /// @brief Зчитати вектор магнітної індукції у фізичних одиницях (Гаус)
    /// @param vec Вихідний вектор у Гаусах (G)
    /// @return true у разі успішного зчитування
    bool readVector(Vector3D& vec);

    /// @brief Отримати коефіцієнт чутливості (LSB per Gauss) залежно від обраного діапазону
    float getSensitivity() const;

private:
    I2CBus& m_bus;
    std::uint8_t m_address;
    Range m_currentRange{Range::G8};
};

#endif // QMC5883L_HPP
