#pragma once

#include <cstdint>
#include <cstddef>
#include <cmath>
#include <array>

// Інтерфейс шини I2C для забезпечення переносності драйвера між різними HAL / платформами
class II2cBus {
public:
    virtual ~II2cBus() = default;

    // Запис 16-бітного значення у 8-бітний регістр пристрою (Big-Endian)
    virtual bool writeRegister16(uint8_t devAddr, uint8_t regAddr, uint16_t value) = 0;

    // Зчитування 16-бітного значення з 8-бітного регістра пристрою (Big-Endian)
    virtual bool readRegister16(uint8_t devAddr, uint8_t regAddr, uint16_t& value) = 0;

    // Послідовний запис масиву байтів
    virtual bool writeBytes(uint8_t devAddr, const uint8_t* data, size_t length) = 0;
};

// Клас-драйвер цифрового монітора живлення INA226
class Ina226 {
public:
    // Адреси регістрів INA226
    enum class Register : uint8_t {
        Config          = 0x00, // Регістр конфігурації
        ShuntVoltage    = 0x01, // Регістр напруги на шунті
        BusVoltage      = 0x02, // Регістр напруги шини
        Power           = 0x03, // Регістр потужності
        Current         = 0x04, // Регістр струму
        Calibration     = 0x05, // Калібрувальний регістр
        MaskEnable      = 0x06, // Маска переривань та статусний регістр
        AlertLimit      = 0x07, // Поріг спрацьовування ALERT
        ManufacturerID  = 0xFE, // ID виробника (0x5449 - TI)
        DieID           = 0xFF  // ID кристала (0x2260)
    };

    // Режими апаратного усереднення вимірювань (AVG[2:0])
    enum class Averaging : uint16_t {
        AVG_1    = 0x0000, // 1 вибірка (без усереднення)
        AVG_4    = 0x0200, // 4 вибірки
        AVG_16   = 0x0400, // 16 вибірок
        AVG_64   = 0x0600, // 64 вибірки
        AVG_128  = 0x0800, // 128 вибірок
        AVG_256  = 0x0A00, // 256 вибірок
        AVG_512  = 0x0C00, // 512 вибірок
        AVG_1024 = 0x0E00  // 1024 вибірки
    };

    // Час перетворення напруги шини (VBUSCT[2:0])
    enum class BusConvTime : uint16_t {
        CT_140us  = 0x0000,
        CT_204us  = 0x0040,
        CT_332us  = 0x0080,
        CT_588us  = 0x00C0,
        CT_1100us = 0x0100, // Стандартне значення 1.1 мс
        CT_2116us = 0x0140,
        CT_4156us = 0x0180,
        CT_8244us = 0x01C0
    };

    // Час перетворення напруги шунта (VSHCT[2:0])
    enum class ShuntConvTime : uint16_t {
        CT_140us  = 0x0000,
        CT_204us  = 0x0008,
        CT_332us  = 0x0010,
        CT_588us  = 0x0018,
        CT_1100us = 0x0020, // Стандартне значення 1.1 мс
        CT_2116us = 0x0028,
        CT_4156us = 0x0030,
        CT_8244us = 0x0038
    };

    // Режим роботи давача (MODE[2:0])
    enum class Mode : uint16_t {
        PowerDown          = 0x0000, // Вимкнено
        ShuntTriggered     = 0x0001, // Одиночний вимір шунта
        BusTriggered       = 0x0002, // Одиночний вимір шини
        ShuntBusTriggered  = 0x0003, // Одиночний вимір шунта й шини
        ShuntContinuous    = 0x0005, // Безперервний вимір шунта
        BusContinuous      = 0x0006, // Безперервний вимір шини
        ShuntBusContinuous = 0x0007  // Безперервний вимір шунта й шини (стандарт)
    };

    // Режим порогового виходу ALERT (Mask/Enable bits [15:10])
    enum class AlertMode : uint16_t {
        None              = 0x0000,
        ShuntOverVoltage  = 0x8000, // SOL: Перевищення напруги шунта
        ShuntUnderVoltage = 0x4000, // SUL: Зниження напруги шунта
        BusOverVoltage    = 0x2000, // BOL: Перевищення напруги шини
        BusUnderVoltage   = 0x1000, // BUL: Зниження напруги шини
        PowerOverLimit    = 0x0800, // POL: Перевищення ліміту потужності
        ConversionReady   = 0x0400  // CNVR: Готовність вимірювання
    };

    // Полярність сигналу ALERT (APOL, bit 1)
    enum class AlertPolarity : uint16_t {
        ActiveLow  = 0x0000, // Активний низький рівень (Open-Collector)
        ActiveHigh = 0x0002  // Активний високий рівень
    };

    // Режим фіксації сигналу ALERT (LEN, bit 0)
    enum class AlertLatch : uint16_t {
        Transparent = 0x0000, // Прозорий (автоматичне скидання)
        Latched     = 0x0001  // Зафіксований (утримується до зчитування Mask/Enable)
    };

    // Структура параметрів конфігурації
    struct Config {
        double shuntResistanceOhms{0.1};          // Опір шунта в Омах (наприклад, 0.1 Ом)
        double maxExpectedCurrentA{10.0};         // Максимальний очікуваний струм в Амперах
        Averaging avg{Averaging::AVG_16};         // Режим усереднення
        BusConvTime vbusTime{BusConvTime::CT_1100us};
        ShuntConvTime vshTime{ShuntConvTime::CT_1100us};
        Mode mode{Mode::ShuntBusContinuous};
    };

    // Структура налаштування порогової події ALERT
    struct AlertConfig {
        AlertMode mode{AlertMode::None};
        double limitValue{0.0};                   // Порогове значення (В, мВ або Вт залежно від режиму)
        AlertPolarity polarity{AlertPolarity::ActiveLow};
        AlertLatch latch{AlertLatch::Latched};
    };

    // Структура для збереження результатів вимірювань
    struct Measurements {
        double busVoltageV{0.0};    // Напруга шини в Вольтах
        double shuntVoltagemV{0.0};  // Напруга на шунті в мілівольтах
        double currentA{0.0};       // Струм в Амперах
        double powerW{0.0};         // Потужність у Ватах
        bool overflow{false};       // Прапорець математичного переповнення (OVF)
        bool alertTriggered{false}; // Прапорець спрацьовування ALERT (AFF)
        bool conversionReady{false};// Прапорець готовності вимірювання (CVRF)
    };

    explicit Ina226(II2cBus& bus, uint8_t address = 0x40);

    // Ініціалізація та перевірка зв'язку з пристроєм
    bool begin(const Config& config);

    // Програмне скидання налаштувань мікросхеми
    bool reset();

    // Перевірка ID виробника (0x5449) та ID кристала (0x2260)
    bool checkDeviceID();

    // Обчислення та запис калібрувального коефіцієнта (CAL)
    bool setCalibration(double shuntResistanceOhms, double maxExpectedCurrentA);

    // Конфігурація режиму та порогу ALERT
    bool configureAlert(const AlertConfig& alertConfig);

    // Зчитування комплексного набору виміряних параметрів
    bool readMeasurements(Measurements& outMeasurements);

    // Окремі методи зчитування фізичних величин
    bool readBusVoltage(double& voltageV);
    bool readShuntVoltage(double& voltagemV);
    bool readCurrent(double& currentA);
    bool readPower(double& powerW);

    // Очищення та зчитування прапорців переривання (скидає зафіксовану лінію ALERT)
    bool clearAlert(uint16_t* outMaskFlags = nullptr);

    // Гетери розрахованих дискретів (LSB) та значення калібрування
    double getCurrentLSB() const { return currentLSB_; }
    double getPowerLSB() const { return powerLSB_; }
    uint16_t getCalibrationValue() const { return calValue_; }

private:
    II2cBus& bus_;
    uint8_t address_;

    double currentLSB_{0.0};
    double powerLSB_{0.0};
    uint16_t calValue_{0};

    // Фіксовані константи LSB з документації Texas Instruments INA226
    static constexpr double SHUNT_VOLTAGE_LSB_V = 0.0000025; // 2.5 µV на молодший розряд
    static constexpr double BUS_VOLTAGE_LSB_V   = 0.00125;   // 1.25 mV на молодший розряд
    static constexpr double CAL_FIXED_FACTOR    = 0.00512;   // Фіксований множник у формулі CAL
};
