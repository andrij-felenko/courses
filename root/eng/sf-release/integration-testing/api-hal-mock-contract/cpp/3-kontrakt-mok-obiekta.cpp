#include <vector>
#include <array>

namespace embedded::hal::testing {

class I2cDriverMock final : public II2cDriver {
public:
    explicit I2cDriverMock(uint16_t expected_dev_addr)
        : expected_addr_(expected_dev_addr) {
        registers_.fill(0x00);
    }

    void setRegister(uint8_t reg, uint8_t val) noexcept {
        registers_[reg] = val;
    }

    uint8_t getRegister(uint8_t reg) const noexcept {
        return registers_[reg];
    }

    void injectStatus(Status status) noexcept {
        injected_status_ = status;
    }

    size_t getCallCount() const noexcept { return call_count_; }

    Status memRead(uint16_t dev_addr,
                   uint16_t mem_addr,
                   size_t mem_addr_size,
                   std::span<uint8_t> data,
                   std::chrono::milliseconds timeout) noexcept override {
        (void)mem_addr_size;
        (void)timeout;
        ++call_count_;

        if (injected_status_ != Status::Ok) {
            Status s = injected_status_;
            injected_status_ = Status::Ok;
            return s;
        }

        if (dev_addr != expected_addr_) {
            return Status::Nack;
        }

        for (size_t i = 0; i < data.size(); ++i) {
            uint8_t reg = static_cast<uint8_t>((mem_addr + i) % registers_.size());
            data[i] = registers_[reg];
        }
        return Status::Ok;
    }

    Status masterTransmit(uint16_t dev_addr,
                          std::span<const uint8_t> data,
                          std::chrono::milliseconds timeout) noexcept override {
        (void)timeout;
        ++call_count_;

        if (injected_status_ != Status::Ok) {
            return injected_status_;
        }

        if (dev_addr != expected_addr_) {
            return Status::Nack;
        }

        if (data.size() >= 2) {
            uint8_t reg = data[0];
            uint8_t val = data[1];
            registers_[reg] = val;
        }
        return Status::Ok;
    }

private:
    uint16_t expected_addr_;
    Status injected_status_{Status::Ok};
    size_t call_count_{0};
    std::array<uint8_t, 256> registers_{};
};

} // namespace embedded::hal::testing
