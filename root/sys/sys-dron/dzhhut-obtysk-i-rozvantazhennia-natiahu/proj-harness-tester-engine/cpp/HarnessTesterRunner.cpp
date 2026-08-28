/**
 * @file HarnessTesterRunner.cpp
 * @brief Повний тестовий запуск діагностики кабельного джгута на C++20.
 */

#include "HarnessTester.hpp"
#include <iostream>
#include <chrono>
#include <thread>

namespace MockHardware {

class VirtualHarnessDriver {
public:
    void setDrive(uint8_t pin, bool level) noexcept {
        driveStates_[pin] = level;
    }

    void setSense(uint8_t pin) noexcept {
        driveStates_[pin] = false;
    }

    bool readLevel(uint8_t pin) noexcept {
        // Симуляція фізичних провідників: якщо активний пін з'єднаний з 'pin', повертаємо true
        for (size_t i = 0; i < DroneHarness::MaxPins; ++i) {
            if (driveStates_[i] && wiring_[i][pin]) {
                return true;
            }
        }
        return false;
    }

    void delayMicroseconds(uint32_t us) noexcept {
        auto start = std::chrono::steady_clock::now();
        while (std::chrono::duration_cast<std::chrono::microseconds>(
                   std::chrono::steady_clock::now() - start).count() < us) {
            // Spin-wait
        }
    }

    uint64_t micros() noexcept {
        return static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::microseconds>(
                std::chrono::steady_clock::now().time_since_epoch()).count());
    }

    void injectWire(uint8_t a, uint8_t b) noexcept {
        wiring_[a][b] = true;
        wiring_[b][a] = true;
    }

    void injectShort(uint8_t a, uint8_t b) noexcept {
        wiring_[a][b] = true;
        wiring_[b][a] = true;
    }

    void injectBreak(uint8_t a, uint8_t b) noexcept {
        wiring_[a][b] = false;
        wiring_[b][a] = false;
    }

private:
    std::array<bool, DroneHarness::MaxPins> driveStates_{};
    std::array<std::array<bool, DroneHarness::MaxPins>, DroneHarness::MaxPins> wiring_{};
};

} // namespace MockHardware

int main() {
    using namespace DroneHarness;

    MockHardware::VirtualHarnessDriver hw;
    constexpr size_t DroneGpsHarnessPins = 6; // JST-GH 6-pin (VCC, TX, RX, SCL, SDA, GND)

    // Конфігурація фізичного кабелю (GPS джгут)
    // 0: VCC_5V <-> 0
    // 1: UART_TX <-> 2 (Cross)
    // 2: UART_RX <-> 1 (Cross)
    // 3: I2C_SCL <-> 3
    // 4: I2C_SDA <-> 4
    // 5: GND     <-> 5
    for (uint8_t i = 0; i < DroneGpsHarnessPins; ++i) {
        hw.injectWire(i, i);
    }

    HarnessEngine<MockHardware::VirtualHarnessDriver> tester(hw, DroneGpsHarnessPins);

    // Встановлення еталонної схеми (прямий 6-піновий кабель)
    AdjacencyMatrix refNetlist(DroneGpsHarnessPins);
    for (uint8_t i = 0; i < DroneGpsHarnessPins; ++i) {
        refNetlist.addConnection(i, i);
    }
    tester.setGoldenNetlist(refNetlist);

    // 1. Тест справного кабелю
    auto res1 = tester.runFullDiagnostic();
    if (res1 && res1->isPassed) {
        std::cout << "[PASS] Еталонний джгут GPS JST-GH успішно верифіковано.\n";
    }

    // 2. Внесення дефекту: обрив лінії SDA (пін 4) та коротке замикання між пінами 1 та 2
    hw.injectBreak(4, 4);
    hw.injectShort(1, 2);

    auto res2 = tester.runFullDiagnostic();
    if (res2) {
        std::cout << "\n[DIAGNOSTIC] Знайдено дефектів: " << res2->totalErrors << "\n";
        std::cout << "  - Обривів: " << res2->openCircuits << "\n";
        std::cout << "  - Закорочень: " << res2->shortCircuits << "\n";

        for (const auto &def : tester.defects()) {
            if (def.type == DefectType::OpenCircuit) {
                std::cout << "  [FAIL] Обрив провідника між пінами: " 
                          << static_cast<int>(def.pinA) << " та " 
                          << static_cast<int>(def.pinB) << "\n";
            } else if (def.type == DefectType::ShortCircuit) {
                std::cout << "  [FAIL] Небажане замикання між пінами: " 
                          << static_cast<int>(def.pinA) << " та " 
                          << static_cast<int>(def.pinB) << "\n";
            }
        }
    }

    return 0;
}
