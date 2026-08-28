#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <vector>
#include <expected>
#include <iostream>
#include <cassert>

namespace hal {

enum class I2cStatus : int8_t {
    Ok = 0,
    ErrNack = -1,
    ErrTimeout = -2,
    ErrBus = -3
};

class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual I2cStatus write_read(uint8_t addr,
                                 std::span<const uint8_t> tx,
                                 std::span<uint8_t> rx) = 0;
};

} // namespace hal

namespace mock {

constexpr uint8_t SensorAddr = 0x68;
constexpr uint8_t ExpectedChipId = 0x5A;

class MockSensorBus final : public hal::II2cBus {
public:
    MockSensorBus() {
        reset();
    }

    void reset() {
        registers_.fill(0);
        registers_[0x00] = ExpectedChipId; // REG_CHIP_ID
        registers_[0x01] = 0x01;           // REG_STATUS: Ready
        registers_[0x02] = 0x09;           // REG_TEMP_MSB (2500 -> 25.00 C)
        registers_[0x03] = 0xC4;           // REG_TEMP_LSB
        registers_[0x04] = 10;             // REG_CALIB_OFFSET
        inject_nack_ = false;
        inject_timeout_ = false;
        transaction_count_ = 0;
    }

    void set_nack_injection(bool enable) noexcept { inject_nack_ = enable; }
    void set_timeout_injection(bool enable) noexcept { inject_timeout_ = enable; }
    [[nodiscard]] uint32_t transaction_count() const noexcept { return transaction_count_; }

    hal::I2cStatus write_read(uint8_t addr,
                              std::span<const uint8_t> tx,
                              std::span<uint8_t> rx) override {
        ++transaction_count_;
        if (addr != SensorAddr || inject_nack_) {
            return hal::I2cStatus::ErrNack;
        }
        if (inject_timeout_) {
            return hal::I2cStatus::ErrTimeout;
        }
        if (tx.empty()) {
            return hal::I2cStatus::ErrBus;
        }

        const uint8_t start_reg = tx[0];

        // Запис даних
        if (tx.size() > 1) {
            for (size_t i = 1; i < tx.size(); ++i) {
                const uint8_t reg = static_cast<uint8_t>(start_reg + (i - 1));
                registers_[reg] = tx[i];
            }
        }

        // Читання даних
        if (!rx.empty()) {
            for (size_t i = 0; i < rx.size(); ++i) {
                const uint8_t reg = static_cast<uint8_t>(start_reg + i);
                rx[i] = registers_[reg];
            }
        }

        return hal::I2cStatus::Ok;
    }

private:
    std::array<uint8_t, 256> registers_{};
    bool inject_nack_{false};
    bool inject_timeout_{false};
    uint32_t transaction_count_{0};
};

} // namespace mock

namespace devices {

enum class DriverError {
    CommunicationFailed,
    InvalidChipId,
    SensorNotReady
};

class TemperatureSensorDriver {
public:
    explicit TemperatureSensorDriver(hal::II2cBus& bus) noexcept
        : bus_(bus), is_initialized_(false), calib_offset_(0) {}

    std::expected<void, DriverError> init() {
        const std::array<uint8_t, 1> reg_id{0x00};
        std::array<uint8_t, 1> chip_id{0};

        if (bus_.write_read(mock::SensorAddr, reg_id, chip_id) != hal::I2cStatus::Ok) {
            return std::unexpected(DriverError::CommunicationFailed);
        }
        if (chip_id[0] != mock::ExpectedChipId) {
            return std::unexpected(DriverError::InvalidChipId);
        }

        const std::array<uint8_t, 1> reg_calib{0x04};
        std::array<uint8_t, 1> calib_val{0};
        if (bus_.write_read(mock::SensorAddr, reg_calib, calib_val) != hal::I2cStatus::Ok) {
            return std::unexpected(DriverError::CommunicationFailed);
        }

        calib_offset_ = static_cast<int8_t>(calib_val[0]);
        is_initialized_ = true;
        return {};
    }

    [[nodiscard]] std::expected<int32_t, DriverError> read_temperature_centi_c() {
        if (!is_initialized_) {
            return std::unexpected(DriverError::CommunicationFailed);
        }

        const std::array<uint8_t, 1> reg_status{0x01};
        std::array<uint8_t, 1> status{0};
        if (bus_.write_read(mock::SensorAddr, reg_status, status) != hal::I2cStatus::Ok) {
            return std::unexpected(DriverError::CommunicationFailed);
        }
        if ((status[0] & 0x01) == 0) {
            return std::unexpected(DriverError::SensorNotReady);
        }

        const std::array<uint8_t, 1> reg_temp{0x02};
        std::array<uint8_t, 2> raw_bytes{0, 0};
        if (bus_.write_read(mock::SensorAddr, reg_temp, raw_bytes) != hal::I2cStatus::Ok) {
            return std::unexpected(DriverError::CommunicationFailed);
        }

        const auto raw_temp = static_cast<int16_t>((raw_bytes[0] << 8) | raw_bytes[1]);
        const int32_t final_temp = static_cast<int32_t>(raw_temp) + calib_offset_;
        return final_temp;
    }

private:
    hal::II2cBus& bus_;
    bool is_initialized_;
    int16_t calib_offset_;
};

} // namespace devices

int main() {
    std::cout << "=== Запуск C++20 тестів драйвера на хості ===\n";

    mock::MockSensorBus mock_bus;
    devices::TemperatureSensorDriver driver(mock_bus);

    // Сценарій 1: Успішна ініціалізація та зчитування
    auto init_res = driver.init();
    assert(init_res.has_value());

    auto temp_res = driver.read_temperature_centi_c();
    assert(temp_res.has_value());
    assert(*temp_res == 2510);
    std::cout << "[PASS] Успішне зчитування: " << *temp_res << " centi-C\n";

    // Сценарій 2: Ін'єкція відмови NACK
    mock_bus.reset();
    mock_bus.set_nack_injection(true);
    devices::TemperatureSensorDriver fault_driver(mock_bus);
    auto fault_res = fault_driver.init();
    assert(!fault_res.has_value());
    assert(fault_res.error() == devices::DriverError::CommunicationFailed);
    std::cout << "[PASS] Перехоплення апаратного збою NACK\n";

    std::cout << "Всі C++ тести пройдено успішно.\n";
    return 0;
}
