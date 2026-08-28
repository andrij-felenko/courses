/**
 * @file HarnessTester.hpp
 * @brief Об'єктно-орієнтований рушій верифікації кабельних мереж (C++20).
 */

#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <vector>
#include <span>
#include <expected>
#include <string_view>
#include <functional>
#include <bitset>
#include <chrono>

namespace DroneHarness {

constexpr size_t MaxPins = 64;

enum class DefectType : uint8_t {
    None = 0,
    OpenCircuit,
    ShortCircuit,
    MiswiredPin,
    IntermittentGlitch
};

struct DefectRecord {
    DefectType type{DefectType::None};
    uint8_t pinA{0};
    uint8_t pinB{0};
    uint32_t glitchDurationUs{0};
};

struct TestSummary {
    bool isPassed{false};
    size_t totalErrors{0};
    size_t openCircuits{0};
    size_t shortCircuits{0};
    size_t miswires{0};
    size_t intermittentGlitches{0};
    std::chrono::microseconds testDuration{0};
};

enum class HardwareError : uint8_t {
    InvalidPinIndex,
    PinDriveFailure,
    SensorTimeout,
    NullInterface
};

/**
 * @brief Концепт для апаратного рівня введення-виведення тестера.
 */
template <typename T>
concept HarnessHardwareDriver = requires(T hw, uint8_t pin, bool level, uint32_t us) {
    { hw.setDrive(pin, level) } -> std::same_as<void>;
    { hw.setSense(pin) } -> std::same_as<void>;
    { hw.readLevel(pin) } -> std::same_as<bool>;
    { hw.delayMicroseconds(us) } -> std::same_as<void>;
    { hw.micros() } -> std::same_as<uint64_t>;
};

/**
 * @brief Клас матриці електричної суміжності провідників.
 */
class AdjacencyMatrix {
public:
    explicit constexpr AdjacencyMatrix(size_t pinCount = 0) noexcept : pinCount_(pinCount) {
        clear();
    }

    constexpr void clear() noexcept {
        for (auto &row : rows_) {
            row.reset();
        }
    }

    constexpr bool addConnection(uint8_t pinA, uint8_t pinB) noexcept {
        if (pinA >= pinCount_ || pinB >= pinCount_) {
            return false;
        }
        rows_[pinA].set(pinB);
        rows_[pinB].set(pinA);
        return true;
    }

    constexpr bool isConnected(uint8_t pinA, uint8_t pinB) const noexcept {
        if (pinA >= pinCount_ || pinB >= pinCount_) {
            return false;
        }
        return rows_[pinA].test(pinB);
    }

    [[nodiscard]] constexpr size_t pinCount() const noexcept { return pinCount_; }
    [[nodiscard]] constexpr const std::bitset<MaxPins>& row(size_t index) const noexcept { return rows_[index]; }
    [[nodiscard]] constexpr std::bitset<MaxPins>& row(size_t index) noexcept { return rows_[index]; }

private:
    size_t pinCount_{0};
    std::array<std::bitset<MaxPins>, MaxPins> rows_{};
};

/**
 * @brief Рушій автоматизованого тестування топології та мікрообривів.
 */
template <HarnessHardwareDriver Driver>
class HarnessEngine {
public:
    HarnessEngine(Driver &hw, size_t pinCount)
        : hw_(hw), pinCount_(pinCount), refMatrix_(pinCount), measuredMatrix_(pinCount) {
        defects_.reserve(64);
    }

    void setGoldenNetlist(const AdjacencyMatrix &netlist) noexcept {
        refMatrix_ = netlist;
    }

    [[nodiscard]] std::expected<void, HardwareError> learnGoldenSample() noexcept {
        auto scanRes = scanPhysicalHarness();
        if (!scanRes) {
            return std::unexpected(scanRes.error());
        }
        refMatrix_ = measuredMatrix_;
        return {};
    }

    [[nodiscard]] std::expected<TestSummary, HardwareError> runFullDiagnostic() noexcept {
        const auto start = hw_.micros();
        defects_.clear();

        auto scanRes = scanPhysicalHarness();
        if (!scanRes) {
            return std::unexpected(scanRes.error());
        }

        TestSummary summary{};
        analyzeNetwork(summary);

        const auto end = hw_.micros();
        summary.testDuration = std::chrono::microseconds(end - start);
        summary.isPassed = (summary.totalErrors == 0);

        return summary;
    }

    [[nodiscard]] std::expected<size_t, HardwareError> runDynamicGlitchMonitor(std::chrono::milliseconds duration) noexcept {
        const uint64_t startUs = hw_.micros();
        const uint64_t durationUs = static_cast<uint64_t>(duration.count()) * 1000ULL;
        size_t glitchCount = 0;

        // Конфігуруємо тестові ланцюги за еталонною схемою
        for (uint8_t i = 0; i < pinCount_; ++i) {
            hw_.setSense(i);
        }

        while ((hw_.micros() - startUs) < durationUs) {
            for (uint8_t i = 0; i < pinCount_; ++i) {
                // Збуджуємо активний пін
                hw_.setDrive(i, true);
                hw_.delayMicroseconds(2);

                for (uint8_t j = 0; j < pinCount_; ++j) {
                    if (refMatrix_.isConnected(i, j) && i != j) {
                        if (!hw_.readLevel(j)) {
                            // Фіксація тривалості мікророзриву
                            const uint64_t glitchStart = hw_.micros();
                            while (!hw_.readLevel(j) && (hw_.micros() - glitchStart < 5000)) {
                                // Очікування відновлення контакту
                            }
                            const uint32_t glitchDur = static_cast<uint32_t>(hw_.micros() - glitchStart);

                            defects_.push_back({
                                .type = DefectType::IntermittentGlitch,
                                .pinA = i,
                                .pinB = j,
                                .glitchDurationUs = (glitchDur > 0) ? glitchDur : 1U
                            });
                            glitchCount++;
                        }
                    }
                }
                hw_.setSense(i);
            }
        }
        return glitchCount;
    }

    [[nodiscard]] std::span<const DefectRecord> defects() const noexcept {
        return defects_;
    }

private:
    std::expected<void, HardwareError> scanPhysicalHarness() noexcept {
        measuredMatrix_.clear();

        for (uint8_t i = 0; i < pinCount_; ++i) {
            hw_.setSense(i);
        }

        for (uint8_t drivePin = 0; drivePin < pinCount_; ++drivePin) {
            hw_.setDrive(drivePin, true);
            hw_.delayMicroseconds(5); // Час заряду ємності лінії

            for (uint8_t sensePin = 0; sensePin < pinCount_; ++sensePin) {
                if (hw_.readLevel(sensePin)) {
                    measuredMatrix_.addConnection(drivePin, sensePin);
                }
            }
            hw_.setSense(drivePin);
        }
        return {};
    }

    void analyzeNetwork(TestSummary &summary) noexcept {
        for (uint8_t i = 0; i < pinCount_; ++i) {
            for (uint8_t j = i + 1; j < pinCount_; ++j) {
                const bool expected = refMatrix_.isConnected(i, j);
                const bool actual = measuredMatrix_.isConnected(i, j);

                if (expected && !actual) {
                    summary.openCircuits++;
                    summary.totalErrors++;
                    defects_.push_back({DefectType::OpenCircuit, i, j, 0});
                } else if (!expected && actual) {
                    summary.shortCircuits++;
                    summary.totalErrors++;
                    defects_.push_back({DefectType::ShortCircuit, i, j, 0});
                }
            }
        }
    }

    Driver &hw_;
    size_t pinCount_{0};
    AdjacencyMatrix refMatrix_;
    AdjacencyMatrix measuredMatrix_;
    std::vector<DefectRecord> defects_;
};

} // namespace DroneHarness
