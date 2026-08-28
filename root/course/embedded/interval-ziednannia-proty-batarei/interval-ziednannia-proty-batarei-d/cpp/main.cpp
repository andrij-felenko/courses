#include <iostream>
#include <iomanip>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>

namespace ble::power {

struct ConnectionParams {
    uint16_t minIntervalUnits{72};  // Крок 1.25 мс (6 .. 3200)
    uint16_t maxIntervalUnits{84};  // Крок 1.25 мс (6 .. 3200)
    uint16_t slaveLatency{18};       // 0 .. 499
    uint16_t timeoutUnits{600};     // Крок 10 мс (10 .. 3200)

    [[nodiscard]] constexpr float minIntervalMs() const noexcept {
        return static_cast<float>(minIntervalUnits) * 1.25f;
    }
    [[nodiscard]] constexpr float maxIntervalMs() const noexcept {
        return static_cast<float>(maxIntervalUnits) * 1.25f;
    }
    [[nodiscard]] constexpr float timeoutMs() const noexcept {
        return static_cast<float>(timeoutUnits) * 10.0f;
    }
    [[nodiscard]] constexpr float effectiveIntervalMs() const noexcept {
        return maxIntervalMs() * static_cast<float>(1 + slaveLatency);
    }
};

struct HardwareProfile {
    float eventChargeMicroCoulombs{15.0f}; // Заряд однієї події, мкКл
    float sleepCurrentMicroAmps{2.0f};      // Струм сну, мкА
    float batteryCapacityMilliAmpHours{225.0f}; // Ємність CR2032
    float batteryInternalResistanceOhms{40.0f}; // Внутрішній опір ESR
    float peakTransceiverCurrentMilliAmps{12.0f}; // Піковий струм TX/RX
    float bulkCapacitanceMicroFarads{47.0f};   // Накопичувальний конденсатор
};

struct SimulationReport {
    bool isValidCoreSpec{false};
    bool isValidAppleIos{false};
    float effectiveIntervalMs{0.0f};
    float averageCurrentMicroAmps{0.0f};
    float batteryLifetimeDays{0.0f};
    float batteryLifetimeYears{0.0f};
    float voltageSagDirectVolts{0.0f};
    float voltageSagBufferedVolts{0.0f};
};

class PowerSimulator {
public:
    [[nodiscard]] static std::optional<SimulationReport> calculate(
        const ConnectionParams& params,
        const HardwareProfile& hw) noexcept
    {
        SimulationReport report{};
        const float minMs = params.minIntervalMs();
        const float maxMs = params.maxIntervalMs();
        const float timeoutMs = params.timeoutMs();
        const float effIntervalMs = params.effectiveIntervalMs();

        report.effectiveIntervalMs = effIntervalMs;

        // 1. Валідація за стандартом Bluetooth Core Spec v5.4
        const bool coreRangeOk = (params.minIntervalUnits >= 6 && params.minIntervalUnits <= 3200) &&
                                 (params.maxIntervalUnits >= 6 && params.maxIntervalUnits <= 3200) &&
                                 (params.minIntervalUnits <= params.maxIntervalUnits) &&
                                 (params.slaveLatency <= 499) &&
                                 (params.timeoutUnits >= 10 && params.timeoutUnits <= 3200);
        const bool coreSafetyOk = timeoutMs > (effIntervalMs * 2.0f);
        report.isValidCoreSpec = coreRangeOk && coreSafetyOk;

        // 2. Валідація за Apple Accessory Design Guidelines
        const bool appleRangeOk = (minMs >= 15.0f) &&
                                  (maxMs >= minMs + 15.0f) &&
                                  (std::fmod(maxMs, 15.0f) < 0.001f || std::fmod(maxMs, 15.0f) > 14.999f) &&
                                  (params.slaveLatency <= 30) &&
                                  (timeoutMs <= 6000.0f) &&
                                  (effIntervalMs <= 2000.0f);
        const bool appleSafetyOk = timeoutMs >= (effIntervalMs * 3.0f);
        report.isValidAppleIos = report.isValidCoreSpec && appleRangeOk && appleSafetyOk;

        // 3. Інтеграл середнього споживання струму
        const float effIntervalSec = effIntervalMs / 1000.0f;
        const float eventCurrentAverageUa = hw.eventChargeMicroCoulombs / effIntervalSec;
        report.averageCurrentMicroAmps = eventCurrentAverageUa + hw.sleepCurrentMicroAmps;

        // 4. Оцінка терміну життя батареї з урахуванням саморозряду (1.2% на рік)
        constexpr float yearlySelfDischargeRate = 0.012f;
        const float selfDischargeCurrentUa = (hw.batteryCapacityMilliAmpHours * 1000.0f * yearlySelfDischargeRate) / 8760.0f;
        const float totalDrainCurrentUa = report.averageCurrentMicroAmps + selfDischargeCurrentUa;
        constexpr float chemicalEfficiency = 0.88f; // Втрата ємності на імпульсах
        const float usableCapacityUah = (hw.batteryCapacityMilliAmpHours * 1000.0f) * chemicalEfficiency;

        const float lifetimeHours = usableCapacityUah / totalDrainCurrentUa;
        report.batteryLifetimeDays = lifetimeHours / 24.0f;
        report.batteryLifetimeYears = report.batteryLifetimeDays / 365.25f;

        // 5. Просідання напруги живлення
        report.voltageSagDirectVolts = (hw.peakTransceiverCurrentMilliAmps / 1000.0f) * hw.batteryInternalResistanceOhms;
        if (hw.bulkCapacitanceMicroFarads > 0.1f) {
            report.voltageSagBufferedVolts = hw.eventChargeMicroCoulombs / hw.bulkCapacitanceMicroFarads;
        } else {
            report.voltageSagBufferedVolts = report.voltageSagDirectVolts;
        }

        return report;
    }
};

} // namespace ble::power

int main() {
    using namespace ble::power;

    const ConnectionParams customParams{
        .minIntervalUnits = 72,  // 90.0 мс
        .maxIntervalUnits = 84,  // 105.0 мс
        .slaveLatency = 18,      // 18 пропусків (T_eff = 1.995 с)
        .timeoutUnits = 600      // 6000 мс
    };

    const HardwareProfile boardProfile{
        .eventChargeMicroCoulombs = 15.0f,
        .sleepCurrentMicroAmps = 2.0f,
        .batteryCapacityMilliAmpHours = 225.0f,
        .batteryInternalResistanceOhms = 40.0f,
        .peakTransceiverCurrentMilliAmps = 12.0f,
        .bulkCapacitanceMicroFarads = 47.0f
    };

    const auto reportOpt = PowerSimulator::calculate(customParams, boardProfile);
    if (!reportOpt.has_value()) {
        std::cerr << "Помилка розрахунку параметрів!\n";
        return 1;
    }

    const auto& res = *reportOpt;
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Результати симуляції BLE енергоспоживання (C++20) ===\n";
    std::cout << "Сумісність з BT Core Spec: " << (res.isValidCoreSpec ? "ТАК" : "НІ") << "\n";
    std::cout << "Сумісність з Apple iOS:    " << (res.isValidAppleIos ? "ТАК" : "НІ") << "\n";
    std::cout << "Ефективний інтервал:       " << res.effectiveIntervalMs << " мс\n";
    std::cout << "Середній струм споживання: " << res.averageCurrentMicroAmps << " мкА\n";
    std::cout << "Час роботи від CR2032:     " << res.batteryLifetimeDays << " діб (" 
              << res.batteryLifetimeYears << " років)\n";
    std::cout << "Просідання без конденсатора: " << res.voltageSagDirectVolts << " В\n";
    std::cout << "Просідання з C_bulk=47мкФ:  " << res.voltageSagBufferedVolts << " В\n";

    return 0;
}
