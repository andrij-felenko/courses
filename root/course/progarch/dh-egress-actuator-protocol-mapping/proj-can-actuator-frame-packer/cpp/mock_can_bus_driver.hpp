#pragma once

#include "can_bus.hpp"
#include <optional>
#include <vector>

// ============================================================================
// ТЕСТОВИЙ КЛАС-ШПИГУН ДРАЙВЕРА CAN (MOCK / SPY)
// ============================================================================

/// @brief Тестовий клас-шпигун драйвера шини CAN.
/// Дозволяє перехоплювати відправлені бінарні кадри в пам'яті для верифікації
/// бітових патернів, порядку байтів та CRC-8 у тестах без фізичного заліза.
/// Також емулює апаратні збої передавача (переповнення черги, аварійне відключення шини).
class MockCanBusDriver final : public ICanBusDriver {
public:
    /// @brief Перехоплення кадру або емуляція апаратного збою.
    [[nodiscard]] std::expected<void, CanBusError> transmit(const CanFrame& frame) override {
        if (should_fail_) {
            return std::unexpected(simulated_error_);
        }
        captured_frames_.push_back(frame);
        return {};
    }

    /// @brief Налаштувати емуляцію апаратного збою шини CAN.
    void simulate_failure(bool fail, CanBusError error = CanBusError::TxQueueFull) noexcept {
        should_fail_ = fail;
        simulated_error_ = error;
    }

    /// @brief Отримати список усіх перехоплених двійкових кадрів.
    [[nodiscard]] const std::vector<CanFrame>& captured_frames() const noexcept {
        return captured_frames_;
    }

    /// @brief Отримати останній перехоплений кадр (якщо був надісланий).
    [[nodiscard]] std::optional<CanFrame> last_frame() const noexcept {
        if (captured_frames_.empty()) {
            return std::nullopt;
        }
        return captured_frames_.back();
    }

    /// @brief Загальна кількість надісланих у шину кадрів.
    [[nodiscard]] size_t frame_count() const noexcept {
        return captured_frames_.size();
    }

    /// @brief Очистити історію перехоплених кадрів та скинути збої.
    void clear() noexcept {
        captured_frames_.clear();
        should_fail_ = false;
    }

private:
    std::vector<CanFrame> captured_frames_;
    bool should_fail_{false};
    CanBusError simulated_error_{CanBusError::TxQueueFull};
};
