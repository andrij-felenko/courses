#include <cstdint>
#include <chrono>
#include <expected>
#include <string_view>
#include <iostream>
#include <format>
#include <span>

/* Клас апаратного драйвера піна з гарантією безпечного знеструмлення (RAII) */
class RelayController {
public:
    enum class Relay { Charge, Discharge };

    explicit RelayController(uint8_t chargePin, uint8_t dischargePin)
        : m_chargePin(chargePin), m_dischargePin(dischargePin) {
        allOff();
    }

    ~RelayController() {
        allOff();
    }

    void setCharge(bool state) noexcept {
        if (state) {
            setPin(m_dischargePin, false);
            delayMicroseconds(10000); // 10 ms break-before-make
        }
        setPin(m_chargePin, state);
    }

    void setDischarge(bool state) noexcept {
        if (state) {
            setPin(m_chargePin, false);
            delayMicroseconds(10000); // 10 ms break-before-make
        }
        setPin(m_dischargePin, state);
    }

    void allOff() noexcept {
        setPin(m_chargePin, false);
        setPin(m_dischargePin, false);
    }

private:
    uint8_t m_chargePin;
    uint8_t m_dischargePin;

    static void setPin(uint8_t pin, bool val) noexcept;
    static void delayMicroseconds(uint32_t us) noexcept;
};

/* Результати випробування діелектричної абсорбції */
struct AbsorptionResult {
    double chargeVoltageVolts{0.0};
    double recoveredVoltageVolts{0.0};
    double dielectricAbsorptionPercent{0.0};
    std::chrono::milliseconds actualChargeTime{0};
    std::chrono::milliseconds actualDischargeTime{0};
};

enum class MeasurementError {
    NoSourceVoltage,
    AdcCommunicationFailed,
    RelayFault,
    AbortedByUser
};

/* Клас вимірювача діелектричної абсорбції */
class DielectricAbsorptionMeter {
public:
    struct Config {
        std::chrono::seconds chargeDuration{900};     // 15 хвилин
        std::chrono::seconds dischargeDuration{5};    // 5 секунд
        std::chrono::seconds recoveryDuration{60};    // 1 хвилина
        double minimumValidChargeVoltage{1.0};       // мінімальна напруга 1 В
    };

    explicit DielectricAbsorptionMeter(RelayController& relays, Config config = {})
        : m_relays(relays), m_config(config) {}

    [[nodiscard]] std::expected<AbsorptionResult, MeasurementError> executeStandardTest() {
        m_relays.allOff();

        // 1. Фаза тривалого заряду
        std::cout << "[DA] Запуск фази заряду (15 хвилин)...\n";
        m_relays.setCharge(true);

        const auto chargeStart = std::chrono::steady_clock::now();
        sleepWithProgress(m_config.chargeDuration, std::chrono::seconds(60));

        const double vCharge = readAdcVoltage();
        if (vCharge < m_config.minimumValidChargeVoltage) {
            m_relays.allOff();
            return std::unexpected(MeasurementError::NoSourceVoltage);
        }

        // 2. Фаза швидкого розряду (КЗ)
        std::cout << "[DA] Запуск фази розряджання (5 секунд)...\n";
        m_relays.setDischarge(true);
        sleepPrecise(m_config.dischargeDuration);

        // 3. Фаза вимірювання відновленої напруги
        m_relays.allOff();
        std::cout << "[DA] Вимірювання відновлення залишкового заряду (60 секунд)...\n";
        sleepWithProgress(m_config.recoveryDuration, std::chrono::seconds(5));

        const double vRecovered = readAdcVoltage();

        // 4. Обчислення відсотка DA
        AbsorptionResult result;
        result.chargeVoltageVolts = vCharge;
        result.recoveredVoltageVolts = vRecovered;
        result.dielectricAbsorptionPercent = (vRecovered / vCharge) * 100.0;
        result.actualChargeTime = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now() - chargeStart);
        result.actualDischargeTime = std::chrono::duration_cast<std::chrono::milliseconds>(
            m_config.dischargeDuration);

        return result;
    }

private:
    RelayController& m_relays;
    Config m_config;

    static double readAdcVoltage() noexcept;
    static void sleepPrecise(std::chrono::milliseconds duration) noexcept;

    static void sleepWithProgress(std::chrono::seconds total, std::chrono::seconds step) {
        auto elapsed = std::chrono::seconds(0);
        while (elapsed < total) {
            const auto chunk = std::min(step, total - elapsed);
            sleepPrecise(chunk);
            elapsed += chunk;
            std::cout << std::format("  ... минуло {} с, V = {:.4f} В\n", 
                                     elapsed.count(), readAdcVoltage());
        }
    }
};
