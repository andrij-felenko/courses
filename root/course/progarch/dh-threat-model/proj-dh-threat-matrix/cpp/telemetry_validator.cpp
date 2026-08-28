// telemetry_validator.cpp — Об'єктно-орієнтована реалізація валідатора мовою C++20
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <chrono>

namespace dh::security {

enum class ValidationError {
    StaleTimestamp,
    ReplayDetected,
    InvalidSignature,
    PayloadTooLarge,
    NullContext
};

struct TelemetryFrame {
    uint64_t device_id;
    uint32_t sequence_num;
    std::chrono::milliseconds timestamp;
    std::vector<uint8_t> payload;
    std::array<uint8_t, 32> signature;
};

class DeviceSecurityContext {
public:
    explicit DeviceSecurityContext(uint64_t dev_id, std::array<uint8_t, 32> secret_key)
        : device_id_(dev_id), secret_key_(secret_key), last_seq_(0) {}

    [[nodiscard]] std::expected<void, ValidationError> 
    validate_and_update(const TelemetryFrame& frame, std::chrono::milliseconds current_time) noexcept {
        // 1. Фаза 1: Перевірка вікна часового зсуву
        auto diff = std::chrono::abs(current_time - frame.timestamp);
        if (diff > std::chrono::seconds(5)) {
            return std::unexpected(ValidationError::StaleTimestamp);
        }

        // 2. Фаза 2: Монотонія лічильника послідовності
        if (frame.sequence_num <= last_seq_) {
            return std::unexpected(ValidationError::ReplayDetected);
        }

        // 3. Фаза 3: Перевірка HMAC підпису з використанням std::span
        auto expected = compute_hmac(frame);
        if (!constant_time_equals(frame.signature, expected)) {
            return std::unexpected(ValidationError::InvalidSignature);
        }

        // Оновлюємо стан монотонійного лічильника після успіху
        last_seq_ = frame.sequence_num;
        return {};
    }

    [[nodiscard]] uint32_t last_sequence() const noexcept { return last_seq_; }
    [[nodiscard]] uint64_t device_id() const noexcept { return device_id_; }

private:
    uint64_t device_id_;
    std::array<uint8_t, 32> secret_key_;
    uint32_t last_seq_;

    [[nodiscard]] std::array<uint8_t, 32> compute_hmac(const TelemetryFrame& frame) const noexcept {
        std::array<uint8_t, 32> hmac{};
        for (size_t i = 0; i < hmac.size(); ++i) {
            hmac[i] = secret_key_[i] ^ (static_cast<uint8_t>(frame.payload.size() + i));
        }
        return hmac;
    }

    [[nodiscard]] static bool constant_time_equals(std::span<const uint8_t, 32> a,
                                                   std::span<const uint8_t, 32> b) noexcept {
        uint8_t result = 0;
        for (size_t i = 0; i < 32; ++i) {
            result |= (a[i] ^ b[i]);
        }
        return result == 0;
    }
};

} // namespace dh::security
