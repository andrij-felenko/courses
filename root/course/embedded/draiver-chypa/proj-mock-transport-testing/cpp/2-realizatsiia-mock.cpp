// C++20: Mock-транспорт на базі концептів та перевірки інваріантів
#include <cstdint>
#include <array>
#include <vector>
#include <span>
#include <expected>
#include <cassert>
#include <iostream>

namespace embedded::testing {

enum class Status : std::int32_t {
    Ok = 0,
    CommFail = -2
};

struct WriteLogEntry {
    std::uint8_t reg;
    std::uint8_t val;
};

class MockTransport {
public:
    static constexpr std::uint8_t RegWhoAmI = 0x0F;
    static constexpr std::uint8_t RegOutXL  = 0x28;
    static constexpr std::uint8_t RegStatus = 0x27;
    static constexpr std::uint8_t ExpectedChipId = 0x33;

    constexpr MockTransport() noexcept {
        reset();
    }

    void reset() noexcept {
        registers_.fill(0);
        write_log_.clear();
        fail_reads_count_ = 0;
        fail_writes_count_ = 0;
        nack_device_address_ = false;
        registers_[RegWhoAmI] = ExpectedChipId;
    }

    void setRawXyz(std::int16_t x, std::int16_t y, std::int16_t z) noexcept {
        registers_[RegOutXL + 0] = static_cast<std::uint8_t>(x & 0xFF);
        registers_[RegOutXL + 1] = static_cast<std::uint8_t>((x >> 8) & 0xFF);
        registers_[RegOutXL + 2] = static_cast<std::uint8_t>(y & 0xFF);
        registers_[RegOutXL + 3] = static_cast<std::uint8_t>((y >> 8) & 0xFF);
        registers_[RegOutXL + 4] = static_cast<std::uint8_t>(z & 0xFF);
        registers_[RegOutXL + 5] = static_cast<std::uint8_t>((z >> 8) & 0xFF);
        registers_[RegStatus] |= (1U << 3); // ZYXDA data ready flag
    }

    void injectReadFailures(std::int32_t count) noexcept {
        fail_reads_count_ = count;
    }

    void setNackAddress(bool enable) noexcept {
        nack_device_address_ = enable;
    }

    Status read(std::uint8_t reg, std::span<std::uint8_t> buffer) noexcept {
        if (nack_device_address_) return Status::CommFail;
        if (fail_reads_count_ > 0) {
            --fail_reads_count_;
            return Status::CommFail;
        }

        for (std::size_t i = 0; i < buffer.size(); ++i) {
            std::uint8_t current_reg = static_cast<std::uint8_t>((reg + i) & 0x7F);
            buffer[i] = registers_[current_reg];
        }
        return Status::Ok;
    }

    Status write(std::uint8_t reg, std::span<const std::uint8_t> buffer) noexcept {
        if (nack_device_address_) return Status::CommFail;
        if (fail_writes_count_ > 0) {
            --fail_writes_count_;
            return Status::CommFail;
        }

        for (std::size_t i = 0; i < buffer.size(); ++i) {
            std::uint8_t current_reg = static_cast<std::uint8_t>((reg + i) & 0x7F);
            registers_[current_reg] = buffer[i];
            write_log_.push_back({current_reg, buffer[i]});
        }
        return Status::Ok;
    }

    void delay_ms(std::uint32_t) noexcept {
        // Миттєве виконання в юніт-тестах
    }

    [[nodiscard]] const std::vector<WriteLogEntry>& writeLog() const noexcept {
        return write_log_;
    }

    [[nodiscard]] std::uint8_t readRegister(std::uint8_t reg) const noexcept {
        return registers_[reg & 0x7F];
    }

private:
    std::array<std::uint8_t, 128> registers_{};
    std::vector<WriteLogEntry> write_log_{};
    std::int32_t fail_reads_count_{0};
    std::int32_t fail_writes_count_{0};
    bool nack_device_address_{false};
};

} // namespace embedded::testing
