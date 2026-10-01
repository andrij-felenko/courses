#include "Ina226.hpp"
#include "OledDisplay.hpp"

#include <iostream>
#include <iomanip>
#include <atomic>
#include <unordered_map>
#include <vector>
#include <thread>
#include <chrono>

// Емуляція апаратного драйвера I2C шини для тестування та демонстрації
class SimulatedI2cBus : public II2cBus {
public:
    SimulatedI2cBus() {
        // Початкові значення регістрів для пристрою INA226 (адреса 0x40)
        inaRegisters_[static_cast<uint8_t>(Ina226::Register::Config)] = 0x4127;
        inaRegisters_[static_cast<uint8_t>(Ina226::Register::ManufacturerID)] = 0x5449;
        inaRegisters_[static_cast<uint8_t>(Ina226::Register::DieID)] = 0x2260;
        
        // Симуляція початкових вимірів: Bus Voltage = 12.0 В (9600 * 1.25 мВ)
        inaRegisters_[static_cast<uint8_t>(Ina226::Register::BusVoltage)] = 9600;
        
        // Shunt Voltage = 15.0 мВ (6000 * 2.5 мкВ)
        inaRegisters_[static_cast<uint8_t>(Ina226::Register::ShuntVoltage)] = 6000;
        
        // Current = 1.5 А (4915 * Current_LSB)
        inaRegisters_[static_cast<uint8_t>(Ina226::Register::Current)] = 4915;
        
        // Power = 18.0 Вт (2359 * Power_LSB)
        inaRegisters_[static_cast<uint8_t>(Ina226::Register::Power)] = 2359;
    }

    bool writeRegister16(uint8_t devAddr, uint8_t regAddr, uint16_t value) override {
        if (devAddr == 0x40) {
            inaRegisters_[regAddr] = value;
            return true;
        }
        return devAddr == 0x3C; // OLED accepts writes
    }

    bool readRegister16(uint8_t devAddr, uint8_t regAddr, uint16_t& value) override {
        if (devAddr == 0x40) {
            auto it = inaRegisters_.find(regAddr);
            if (it != inaRegisters_.end()) {
                value = it->second;
                // Читання Mask/Enable (0x06) скидає прапорець AFF (біт 4)
                if (regAddr == static_cast<uint8_t>(Ina226::Register::MaskEnable)) {
                    inaRegisters_[regAddr] &= ~0x0010;
                }
                return true;
            }
        }
        return false;
    }

    bool writeBytes(uint8_t devAddr, const uint8_t* data, size_t length) override {
        (void)devAddr;
        (void)data;
        (void)length;
        return true; // Симуляція успішного запису блоку даних у SSD1306
    }

    // Симуляція зміни навантаження в колі
    void simulateLoadChange(double voltageV, double currentA) {
        // Bus Voltage LSB = 1.25 mV
        uint16_t busRaw = static_cast<uint16_t>(voltageV / 0.00125);
        inaRegisters_[static_cast<uint8_t>(Ina226::Register::BusVoltage)] = busRaw;

        // Current LSB ~ 10.0 / 32768 = 0.00030517578125 A
        double currentLSB = 10.0 / 32768.0;
        int16_t currRaw = static_cast<int16_t>(currentA / currentLSB);
        inaRegisters_[static_cast<uint8_t>(Ina226::Register::Current)] = static_cast<uint16_t>(currRaw);

        // Power LSB = 25 * currentLSB
        double powerLSB = 25.0 * currentLSB;
        double powerW = voltageV * currentA;
        uint16_t powerRaw = static_cast<uint16_t>(powerW / powerLSB);
        inaRegisters_[static_cast<uint8_t>(Ina226::Register::Power)] = powerRaw;

        // Перевірка перевищення порогу потужності (15.0 Вт) та встановлення прапорця AFF
        uint16_t alertLimitRaw = inaRegisters_[static_cast<uint8_t>(Ina226::Register::AlertLimit)];
        if (powerRaw > alertLimitRaw && alertLimitRaw > 0) {
            inaRegisters_[static_cast<uint8_t>(Ina226::Register::MaskEnable)] |= 0x0010; // Біт 4: AFF
        }
    }

private:
    std::unordered_map<uint8_t, uint16_t> inaRegisters_;
};

// Прапорець зовнішнього апаратного переривання EXTI від лінії ALERT INA226
static std::atomic<bool> g_extiAlertFlag{false};

// Обробник переривання EXTI (ISR - Interrupt Service Routine)
void extiGpioAlertIsr() {
    // В обробнику переривання виконуються лише мінімальні атомарні операції
    g_extiAlertFlag.store(true, std::memory_order_relaxed);
}

int main() {
    std::cout << "=== Ініціалізація системи моніторингу живлення (INA226 + OLED + EXTI) ===" << std::endl;

    SimulatedI2cBus i2cBus;
    Ina226 ina226(i2cBus, 0x40);
    OledDisplay oled(i2cBus, 0x3C);

    // 1. Конфігурація монітора живлення INA226
    Ina226::Config inaConfig;
    inaConfig.shuntResistanceOhms = 0.1;  // Шунт 100 мОм
    inaConfig.maxExpectedCurrentA = 10.0; // Максимальний струм 10 А
    inaConfig.avg = Ina226::Averaging::AVG_16;
    inaConfig.vbusTime = Ina226::BusConvTime::CT_1100us;
    inaConfig.vshTime = Ina226::ShuntConvTime::CT_1100us;
    inaConfig.mode = Ina226::Mode::ShuntBusContinuous;

    if (!ina226.begin(inaConfig)) {
        std::cerr << "[ПОМИЛКА] Не вдалося ініціалізувати INA226!" << std::endl;
        return -1;
    }
    std::cout << "[ОК] INA226 ініціалізовано. CAL = " << ina226.getCalibrationValue() 
              << ", Current LSB = " << ina226.getCurrentLSB() * 1e6 << " мкА/дискрет" << std::endl;

    // 2. Налаштування порогової події ALERT на перевищення потужності 15.0 Вт
    Ina226::AlertConfig alertConfig;
    alertConfig.mode = Ina226::AlertMode::PowerOverLimit;
    alertConfig.limitValue = 15.0; // Поріг 15 Вт
    alertConfig.polarity = Ina226::AlertPolarity::ActiveLow;
    alertConfig.latch = Ina226::AlertLatch::Latched;

    if (!ina226.configureAlert(alertConfig)) {
        std::cerr << "[ПОМИЛКА] Не вдалося налаштувати порогові значення ALERT!" << std::endl;
        return -1;
    }
    std::cout << "[ОК] Порогову подію ALERT налаштовано на PowerOverLimit (15.0 Вт)." << std::endl;

    // 3. Ініціалізація OLED-дисплея
    if (!oled.begin()) {
        std::cerr << "[ПОМИЛКА] Не вдалося ініціалізувати OLED-дисплей!" << std::endl;
        return -1;
    }
    std::cout << "[ОК] OLED-дисплей ініціалізовано." << std::endl;

    std::cout << "\n=== Запуск головного циклу моніторингу ===" << std::endl;

    // Симуляція кількох циклів вимірювання
    for (int cycle = 1; cycle <= 5; ++cycle) {
        std::cout << "\n--- Цикл #" << cycle << " ---" << std::endl;

        // Симуляція зміни струму в колі на 4-му циклі для виклику апаратного переривання
        if (cycle == 4) {
            std::cout << "[СИМУЛЯЦІЯ] Стрибок навантаження: 12.0 В, 1.5 А -> Потужність = 18.0 Вт (Перевищення 15 Вт!)" << std::endl;
            i2cBus.simulateLoadChange(12.0, 1.5);
            // Апаратна лінія ALERT падає в 0 -> контролер викликає EXTI ISR
            extiGpioAlertIsr();
        } else {
            i2cBus.simulateLoadChange(12.0, 0.8); // 9.6 Вт - в межах норми
        }

        // Обробка зовнішнього апаратного переривання EXTI від лінії ALERT
        if (g_extiAlertFlag.load(std::memory_order_relaxed)) {
            std::cout << "[EXTI ISR] Отримано сигнал переривання від лінії ALERT INA226!" << std::endl;

            // Зчитуємо та очищаємо статус переривання
            uint16_t maskFlags = 0;
            if (ina226.clearAlert(&maskFlags)) {
                bool aff = (maskFlags & 0x0010) != 0;
                bool ovf = (maskFlags & 0x0004) != 0;
                std::cout << "[DIAG] Прапорці Mask/Enable: 0x" << std::hex << maskFlags << std::dec
                          << " (AFF: " << aff << ", OVF: " << ovf << ")" << std::endl;
            }

            // Зчитати актуальні виміри після аварійної події
            Ina226::Measurements m;
            if (ina226.readMeasurements(m)) {
                std::cout << std::fixed << std::setprecision(3);
                std::cout << "[АВАРІЯ] V: " << m.busVoltageV << " В | I: " << m.currentA
                          << " А | P: " << m.powerW << " Вт" << std::endl;

                // Оновлення OLED із позначкою тривоги
                oled.displayPowerMetrics(m.busVoltageV, m.currentA, m.powerW, true);
                oled.update();
            }

            // Скидання прапорця переривання
            g_extiAlertFlag.store(false, std::memory_order_relaxed);
        } else {
            // Штатне зчитування вимірів без виходу за межі
            Ina226::Measurements m;
            if (ina226.readMeasurements(m)) {
                std::cout << std::fixed << std::setprecision(3);
                std::cout << "[НОРМА] V: " << m.busVoltageV << " В | I: " << m.currentA
                          << " А | P: " << m.powerW << " Вт" << std::endl;

                // Оновлення OLED у штатному режимі
                oled.displayPowerMetrics(m.busVoltageV, m.currentA, m.powerW, false);
                oled.update();
            }
        }
    }

    std::cout << "\n=== Моніторинг успішно завершено ===" << std::endl;
    return 0;
}
