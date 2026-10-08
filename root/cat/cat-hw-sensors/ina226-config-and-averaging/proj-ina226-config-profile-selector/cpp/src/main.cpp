#include "ina226_profile_manager.hpp"
#include <iostream>
#include <iomanip>
#include <unordered_map>
#include <cmath>

// Клас імітатора I2C-шини для емуляції фізичних регістрів INA226
class SimulatedI2cBus : public ina226::II2cBus {
public:
    SimulatedI2cBus() {
        // Початкова ініціалізація регістрів за замовчуванням
        registers_[static_cast<uint8_t>(ina226::Register::ManufacturerId)] = 0x5449;
        registers_[static_cast<uint8_t>(ina226::Register::DieId)]          = 0x2260;
        registers_[static_cast<uint8_t>(ina226::Register::Configuration)]   = 0x4127;
    }

    bool writeRegister16(uint8_t devAddr, uint8_t regAddr, uint16_t value) override {
        (void)devAddr;
        registers_[regAddr] = value;
        return true;
    }

    bool readRegister16(uint8_t devAddr, uint8_t regAddr, uint16_t& value) override {
        (void)devAddr;
        auto it = registers_.find(regAddr);
        if (it != registers_.end()) {
            value = it->second;
            return true;
        }
        value = 0x0000;
        return true;
    }

    // Допоміжний метод для моделювання фізичного струму та напруги
    void simulateLoad(double currentA, double voltageV, double shuntR, double currentLsb) {
        double shuntMv = currentA * shuntR * 1000.0;

        auto rawShunt = static_cast<int16_t>(std::round(shuntMv / 0.0025));
        registers_[static_cast<uint8_t>(ina226::Register::ShuntVoltage)] = static_cast<uint16_t>(rawShunt);

        auto rawBus = static_cast<uint16_t>(std::round(voltageV / 0.00125));
        registers_[static_cast<uint8_t>(ina226::Register::BusVoltage)] = rawBus;

        auto rawCurrent = static_cast<int16_t>(std::round(currentA / currentLsb));
        registers_[static_cast<uint8_t>(ina226::Register::Current)] = static_cast<uint16_t>(rawCurrent);

        double powerW = voltageV * currentA;
        auto rawPower = static_cast<uint16_t>(std::round(powerW / (25.0 * currentLsb)));
        registers_[static_cast<uint8_t>(ina226::Register::Power)] = rawPower;

        registers_[static_cast<uint8_t>(ina226::Register::MaskEnable)] |= 
            ina226::AlertMask::CONVERSION_READY | 
            ina226::AlertStatusFlag::CONVR_READY |
            (currentA > 2.5 ? (ina226::AlertMask::SHUNT_OVER_LIMIT | ina226::AlertStatusFlag::ALERT_FUNCTION) : 0);
    }

private:
    std::unordered_map<uint8_t, uint16_t> registers_;
};

int main() {
    std::cout << "=== Система адаптивного моніторингу живлення INA226 ===" << std::endl;

    SimulatedI2cBus i2cBus;
    constexpr double SHUNT_OHMS = 0.002;
    constexpr double MAX_CURRENT_A = 10.0;
    constexpr double CURRENT_LSB = MAX_CURRENT_A / 32768.0;

    ina226::Ina226ProfileManager profileManager(i2cBus, 0x40, SHUNT_OHMS, MAX_CURRENT_A);

    // Робочий профіль для стабільного стану (високе усереднення, низький шум)
    ina226::SamplingProfile steadyProfile{
        "Стаціонарний (AVG_128, 1.1ms)",
        ina226::AveragingMode::AVG_128,
        ina226::ConversionTime::TIME_1100US,
        ina226::ConversionTime::TIME_1100US,
        ina226::OperatingMode::SHUNT_BUS_CONTINUOUS
    };

    // Робочий профіль для пікових навантажень (мінімальна затримка)
    ina226::SamplingProfile dynamicProfile{
        "Динамічний (AVG_4, 140us)",
        ina226::AveragingMode::AVG_4,
        ina226::ConversionTime::TIME_140US,
        ina226::ConversionTime::TIME_140US,
        ina226::OperatingMode::SHUNT_BUS_CONTINUOUS
    };

    // Реєстрація зворотного виклику для сповіщення про зміну профілю
    profileManager.setProfileChangeCallback([](const ina226::SamplingProfile& oldProf,
                                               const ina226::SamplingProfile& newProf) {
        std::cout << "\n[ПОДІЯ: ЗМІНА ПРОФІЛЮ] " << oldProf.name
                  << " ---> " << newProf.name << std::endl;
    });

    // Реєстрація зворотного виклику для апаратних подій ALERT
    profileManager.setAlertCallback([](const ina226::AlertEvent& event) {
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "[ОБРОБНИК ALERT] Причина: ";
        switch (event.type) {
            case ina226::AlertEventType::ConversionReady:
                std::cout << "Готовність даних (Conversion Ready)";
                break;
            case ina226::AlertEventType::OverCurrentLimit:
                std::cout << "Перевищення ліміту струму!";
                break;
            default:
                std::cout << "Інша подія давача";
                break;
        }
        std::cout << " | U: " << event.busVoltageVolts << " В"
                  << " | I: " << event.currentAmperes << " А"
                  << " | P: " << event.powerWatts << " Вт" << std::endl;
    });

    // Ініціалізація пристрою та I2C
    if (!profileManager.begin()) {
        std::cerr << "Помилка зв'язку з давачем INA226!" << std::endl;
        return 1;
    }

    // Налаштування адаптивних порогів перемикання (Поріг струму = 1.5 А)
    profileManager.setAdaptiveThresholds(1.5, dynamicProfile, steadyProfile);
    std::cout << "Початковий профіль: " << profileManager.getCurrentProfile().name << std::endl;

    // Сценарій 1: Малий струм (0.5 А) -> Робота у стаціонарному режимі
    std::cout << "\n--- Сценарій 1: Номінальний режим (I = 0.5 А) ---" << std::endl;
    i2cBus.simulateLoad(0.5, 12.0, SHUNT_OHMS, CURRENT_LSB);
    profileManager.handleAlertInterrupt();

    // Сценарій 2: Різке зростання струму (2.8 А) -> Адаптивний перехід на динамічний профіль
    std::cout << "\n--- Сценарій 2: Стрибок навантаження (I = 2.8 А) ---" << std::endl;
    i2cBus.simulateLoad(2.8, 11.8, SHUNT_OHMS, CURRENT_LSB);
    profileManager.handleAlertInterrupt();

    // Сценарій 3: Тривала робота при високому струмі (3.0 А) -> Профіль залишається динамічним
    std::cout << "\n--- Сценарій 3: Робота під навантаженням (I = 3.0 А) ---" << std::endl;
    i2cBus.simulateLoad(3.0, 11.7, SHUNT_OHMS, CURRENT_LSB);
    profileManager.handleAlertInterrupt();

    // Сценарій 4: Спад струму (0.6 А) -> Повернення до стаціонарного профілю
    std::cout << "\n--- Сценарій 4: Зниження навантаження (I = 0.6 А) ---" << std::endl;
    i2cBus.simulateLoad(0.6, 12.0, SHUNT_OHMS, CURRENT_LSB);
    profileManager.handleAlertInterrupt();

    std::cout << "\n=== Моделювання успішно завершено ===" << std::endl;
    return 0;
}
