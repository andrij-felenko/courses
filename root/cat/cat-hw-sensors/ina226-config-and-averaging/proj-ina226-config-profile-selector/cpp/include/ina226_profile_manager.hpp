#ifndef INA226_PROFILE_MANAGER_HPP
#define INA226_PROFILE_MANAGER_HPP

#include "ina226_types.hpp"
#include <functional>
#include <utility>

namespace ina226 {

// Абстрактний інтерфейс I2C-шини для апаратної незалежності
class II2cBus {
public:
    virtual ~II2cBus() = default;

    // Запис 16-бітного значення в регістр пристрою (Big-Endian)
    virtual bool writeRegister16(uint8_t devAddr, uint8_t regAddr, uint16_t value) = 0;

    // Читання 16-бітного значення з регістру пристрою (Big-Endian)
    virtual bool readRegister16(uint8_t devAddr, uint8_t regAddr, uint16_t& value) = 0;
};

// Менеджер робочих профілів та переривань давача INA226
class Ina226ProfileManager {
public:
    using AlertCallback = std::function<void(const AlertEvent&)>;
    using ProfileChangeCallback = std::function<void(const SamplingProfile& oldProfile, const SamplingProfile& newProfile)>;

    // Конструктор класу
    explicit Ina226ProfileManager(II2cBus& i2cBus,
                                  uint8_t i2cAddress = 0x40,
                                  double shuntResistorOhms = 0.002,
                                  double maxExpectedCurrentA = 10.0);

    // Ініціалізація давача, перевірка ID та первинне калібрування
    bool begin();

    // Скидання давача до заводських налаштувань
    bool reset();

    // Обчислення та запис калібрувального регістру
    bool configureCalibration(double maxCurrentAmperes);

    // Встановлення нового профілю усереднення та часу перетворення
    bool setProfile(const SamplingProfile& profile);

    // Отримання поточного активного профілю
    [[nodiscard]] SamplingProfile getCurrentProfile() const noexcept { return currentProfile_; }

    // Конфігурація маски переривань ALERT та порогового значення
    bool setAlertMask(uint16_t maskFlags, uint16_t alertLimitRaw = 0);

    // Реєстрація зворотних викликів
    void setAlertCallback(AlertCallback callback) { alertCallback_ = std::move(callback); }
    void setProfileChangeCallback(ProfileChangeCallback callback) { profileChangeCallback_ = std::move(callback); }

    // Налаштування адаптивного перемикання профілів за пороговим струмом
    bool setAdaptiveThresholds(double highCurrentThresholdA,
                               const SamplingProfile& dynamicProfile,
                               const SamplingProfile& steadyProfile);

    // Неблокуюча обробка апаратного переривання ALERT
    void handleAlertInterrupt();

    // Читання виміряних величин
    bool readBusVoltage(double& voltageVolts);
    bool readShuntVoltage(double& voltageMv);
    bool readCurrent(double& currentAmperes);
    bool readPower(double& powerWatts);

private:
    II2cBus& bus_;
    uint8_t address_;
    double shuntResistorOhms_;
    double maxExpectedCurrentA_;
    double currentLsb_{0.0};
    uint16_t calibrationValue_{0};

    SamplingProfile currentProfile_{"Default", AveragingMode::AVG_16, ConversionTime::TIME_1100US, ConversionTime::TIME_1100US, OperatingMode::SHUNT_BUS_CONTINUOUS};
    
    // Параметри адаптивного режимного моніторингу
    bool adaptiveEnabled_{false};
    double highCurrentThresholdA_{0.0};
    SamplingProfile dynamicProfile_{};
    SamplingProfile steadyProfile_{};

    // Callback-обробники
    AlertCallback alertCallback_{nullptr};
    ProfileChangeCallback profileChangeCallback_{nullptr};

    // Допоміжні методи для I2C
    bool writeRegister(Register reg, uint16_t value);
    bool readRegister(Register reg, uint16_t& value);
};

} // namespace ina226

#endif // INA226_PROFILE_MANAGER_HPP
