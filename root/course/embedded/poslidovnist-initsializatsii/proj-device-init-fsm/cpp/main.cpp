#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <chrono>
#include <string_view>

namespace embedded {

using namespace std::chrono_literals;

enum class BusStatus {
    Ok = 0,
    Nack,
    Timeout
};

enum class FsmState {
    PowerOnDelay,
    SendReset,
    PollReady,
    VerifyChipId,
    WriteConfig,
    ReadbackVerify,
    Activate,
    SettlingDelay,
    Ready,
    RetryBackoff,
    FaultSafe
};

struct RegConfigEntry {
    uint8_t reg;
    uint8_t val;
    uint8_t mask;
};

// Інтерфейс апаратної шини I2C
class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual BusStatus write(uint8_t dev_addr, uint8_t reg, uint8_t val) = 0;
    virtual BusStatus read(uint8_t dev_addr, uint8_t reg, uint8_t &val) = 0;
    virtual void recover() = 0;
};

// Драйвер надійного запуску пристрою
class SafeSensorDriver {
public:
    static constexpr uint8_t DevAddress = 0x68;
    static constexpr uint8_t RegChipId = 0x00;
    static constexpr uint8_t ExpectedChipId = 0xEA;
    static constexpr uint8_t RegResetCtrl = 0x10;
    static constexpr uint8_t BitSwReset = 1U << 7;
    static constexpr uint8_t BitDeviceReady = 1U << 0;
    static constexpr uint8_t RegPwrMode = 0x1A;
    static constexpr uint8_t ValPwrActive = 0x01;

    static constexpr auto TimePorBoot = 25ms;
    static constexpr auto TimeResetWait = 10ms;
    static constexpr auto TimePollTimeout = 100ms;
    static constexpr auto TimeAnalogSettle = 15ms;
    static constexpr auto BaseBackoff = 50ms;
    static constexpr uint8_t MaxRetries = 3;

    explicit SafeSensorDriver(II2cBus &bus) : bus_(bus) {}

    void reset() {
        state_ = FsmState::PowerOnDelay;
        state_enter_time_ = get_current_time();
        timeout_duration_ = 0ms;
        config_idx_ = 0;
        retry_count_ = 0;
        fault_reason_ = {};
    }

    void step() {
        const auto now = get_current_time();
        uint8_t val = 0;

        switch (state_) {
            case FsmState::PowerOnDelay:
                if (now - state_enter_time_ >= TimePorBoot) {
                    state_ = FsmState::SendReset;
                }
                break;

            case FsmState::SendReset:
                if (bus_.write(DevAddress, RegResetCtrl, BitSwReset) == BusStatus::Ok) {
                    state_ = FsmState::PollReady;
                    state_enter_time_ = now;
                } else {
                    trigger_retry_or_fail("NACK on SW_RESET");
                }
                break;

            case FsmState::PollReady:
                if (now - state_enter_time_ < TimeResetWait) {
                    break;
                }
                if (bus_.read(DevAddress, RegResetCtrl, val) == BusStatus::Ok) {
                    if ((val & BitSwReset) == 0 && (val & BitDeviceReady)) {
                        state_ = FsmState::VerifyChipId;
                        break;
                    }
                }
                if (now - state_enter_time_ >= TimePollTimeout) {
                    trigger_retry_or_fail("Timeout waiting for ready flag");
                }
                break;

            case FsmState::VerifyChipId:
                if (bus_.read(DevAddress, RegChipId, val) == BusStatus::Ok) {
                    if (val == ExpectedChipId) {
                        config_idx_ = 0;
                        state_ = FsmState::WriteConfig;
                    } else {
                        trigger_retry_or_fail("Invalid CHIP_ID");
                    }
                } else {
                    trigger_retry_or_fail("Bus error reading CHIP_ID");
                }
                break;

            case FsmState::WriteConfig:
                if (config_idx_ < config_table_.size()) {
                    const auto &entry = config_table_[config_idx_];
                    if (bus_.write(DevAddress, entry.reg, entry.val) == BusStatus::Ok) {
                        state_ = FsmState::ReadbackVerify;
                    } else {
                        trigger_retry_or_fail("Write config error");
                    }
                } else {
                    state_ = FsmState::Activate;
                }
                break;

            case FsmState::ReadbackVerify: {
                const auto &entry = config_table_[config_idx_];
                if (bus_.read(DevAddress, entry.reg, val) == BusStatus::Ok) {
                    if ((val & entry.mask) == (entry.val & entry.mask)) {
                        config_idx_++;
                        state_ = FsmState::WriteConfig;
                    } else {
                        trigger_retry_or_fail("Read-back verify mismatch");
                    }
                } else {
                    trigger_retry_or_fail("Read-back bus error");
                }
                break;
            }

            case FsmState::Activate:
                if (bus_.write(DevAddress, RegPwrMode, ValPwrActive) == BusStatus::Ok) {
                    state_ = FsmState::SettlingDelay;
                    state_enter_time_ = now;
                } else {
                    trigger_retry_or_fail("Activation command error");
                }
                break;

            case FsmState::SettlingDelay:
                if (now - state_enter_time_ >= TimeAnalogSettle) {
                    state_ = FsmState::Ready;
                    retry_count_ = 0;
                }
                break;

            case FsmState::RetryBackoff:
                if (now - state_enter_time_ >= timeout_duration_) {
                    state_ = FsmState::PowerOnDelay;
                    state_enter_time_ = now;
                }
                break;

            case FsmState::Ready:
            case FsmState::FaultSafe:
            default:
                break;
        }
    }

    [[nodiscard]] bool is_ready() const noexcept {
        return state_ == FsmState::Ready;
    }

    [[nodiscard]] bool is_fault() const noexcept {
        return state_ == FsmState::FaultSafe;
    }

    [[nodiscard]] std::string_view fault_reason() const noexcept {
        return fault_reason_;
    }

private:
    static std::chrono::milliseconds get_current_time();

    void trigger_retry_or_fail(std::string_view reason) {
        retry_count_++;
        if (retry_count_ <= MaxRetries) {
            bus_.recover();
            state_ = FsmState::RetryBackoff;
            state_enter_time_ = get_current_time();
            timeout_duration_ = BaseBackoff * (1U << (retry_count_ - 1U));
        } else {
            state_ = FsmState::FaultSafe;
            fault_reason_ = reason;
        }
    }

    II2cBus &bus_;
    FsmState state_{FsmState::PowerOnDelay};
    std::chrono::milliseconds state_enter_time_{0};
    std::chrono::milliseconds timeout_duration_{0};
    size_t config_idx_{0};
    uint8_t retry_count_{0};
    std::string_view fault_reason_{};

    static constexpr std::array<RegConfigEntry, 2> config_table_{{
        {0x18, 0x02, 0x0F}, // Range ±4g
        {0x19, 0x34, 0x7F}  // ODR 100Hz + DLPF
    }};
};

} // namespace embedded
