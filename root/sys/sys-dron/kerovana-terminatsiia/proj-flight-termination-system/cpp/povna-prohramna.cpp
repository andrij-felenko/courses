#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <cmath>

namespace fts::embedded {

inline constexpr uint32_t MagicHeader       = 0x5AA5F751U;
inline constexpr uint32_t ArmTimeoutMs      = 2500U;
inline constexpr uint32_t MinArmTimeMs      = 80U;
inline constexpr uint32_t SquibPulseMs      = 60U;
inline constexpr uint32_t MotorSpindownMs   = 70U;

inline constexpr float SpinRateThreshold    = 7.85F;  // 450 deg/s in rad/s
inline constexpr float FreefallThresholdG   = 0.25F;  // 0.25 g
inline constexpr uint32_t DwellTimeMs       = 350U;

enum class State : uint8_t {
    Safe = 0,
    Armed,
    Triggered,
    LatchedKill
};

enum class Command : uint8_t {
    None      = 0x00,
    Arm       = 0xA5,
    Terminate = 0x5A,
    Heartbeat = 0x55,
    Disarm    = 0x33
};

enum class ProcessingError {
    BufferTooSmall,
    InvalidMagic,
    ChecksumMismatch,
    ReplayDetected,
    AuthFailed
};

struct [[gnu::packed]] RawPacket {
    uint32_t magic;
    uint32_t seq_num;
    uint32_t timestamp_ms;
    Command  command;
    uint8_t  reserved[3];
    uint64_t auth_token;
    uint32_t crc32;
};

struct ImuSample {
    float gx{0.0F}, gy{0.0F}, gz{0.0F};
    float ax{0.0F}, ay{0.0F}, az{0.0F};
};

class HardwareInterlockDriver {
public:
    static void setMotorKill(bool active) noexcept {
        // Керування eFuse та заземленням ШІМ/DShot
    }

    static void setSquibArmGate(bool active) noexcept {
        // Верхній ключ зарядної ємності
    }

    static void setSquibFireGate(bool active) noexcept {
        // Нижній ключ струмового імпульсу
    }
};

class WatchdogEngine {
public:
    constexpr WatchdogEngine(uint64_t key1, uint64_t key2) noexcept
        : key1_(key1), key2_(key2) {}

    [[nodiscard]] std::expected<void, ProcessingError> processRadioPacket(
        std::span<const uint8_t> buffer,
        uint32_t nowMs) noexcept
    {
        if (buffer.size() < sizeof(RawPacket)) {
            return std::unexpected(ProcessingError::BufferTooSmall);
        }

        const auto& pkt = *reinterpret_cast<const RawPacket*>(buffer.data());

        if (pkt.magic != MagicHeader) {
            return std::unexpected(ProcessingError::InvalidMagic);
        }

        const uint32_t calcCrc = computeCrc32(buffer.first(sizeof(RawPacket) - sizeof(uint32_t)));
        if (calcCrc != pkt.crc32) {
            return std::unexpected(ProcessingError::ChecksumMismatch);
        }

        if (pkt.seq_num <= lastValidSeq_) {
            return std::unexpected(ProcessingError::ReplayDetected);
        }

        if (computeHmac(pkt, key1_, key2_) != pkt.auth_token) {
            return std::unexpected(ProcessingError::AuthFailed);
        }

        lastValidSeq_ = pkt.seq_num;
        handleCommand(pkt.command, nowMs);
        return {};
    }

    void update(const ImuSample& imu, uint32_t nowMs) noexcept {
        // 1. Контроль таймауту взведення
        if (state_ == State::Armed) {
            if (nowMs - armStartMs_ > ArmTimeoutMs) {
                state_ = State::Safe;
            }
        }

        // 2. Детектування штопору
        if (state_ == State::Safe || state_ == State::Armed) {
            const float spinRate = std::sqrt(imu.gx * imu.gx + imu.gy * imu.gy + imu.gz * imu.gz);
            const float accelG   = std::sqrt(imu.ax * imu.ax + imu.ay * imu.ay + imu.az * imu.az);

            if (spinRate > SpinRateThreshold && accelG < FreefallThresholdG) {
                if (!inSpinAnomaly_) {
                    inSpinAnomaly_ = true;
                    spinStartMs_ = nowMs;
                } else if (nowMs - spinStartMs_ >= DwellTimeMs) {
                    triggerTermination(nowMs);
                }
            } else {
                inSpinAnomaly_ = false;
            }
        }

        // 3. Керована часова послідовність
        if (state_ == State::Triggered) {
            const uint32_t elapsed = nowMs - triggerStartMs_;

            if (elapsed >= MotorSpindownMs && elapsed < (MotorSpindownMs + SquibPulseMs)) {
                HardwareInterlockDriver::setSquibArmGate(true);
                HardwareInterlockDriver::setSquibFireGate(true);
            } else if (elapsed >= (MotorSpindownMs + SquibPulseMs)) {
                HardwareInterlockDriver::setSquibArmGate(false);
                HardwareInterlockDriver::setSquibFireGate(false);
                state_ = State::LatchedKill;
            }
        }

        if (state_ == State::LatchedKill) {
            HardwareInterlockDriver::setMotorKill(true);
        }
    }

    [[nodiscard]] State getState() const noexcept { return state_; }

private:
    void handleCommand(Command cmd, uint32_t nowMs) noexcept {
        switch (state_) {
            case State::Safe:
                if (cmd == Command::Arm) {
                    state_ = State::Armed;
                    armStartMs_ = nowMs;
                }
                break;

            case State::Armed:
                if (cmd == Command::Terminate) {
                    const uint32_t delta = nowMs - armStartMs_;
                    if (delta >= MinArmTimeMs && delta <= ArmTimeoutMs) {
                        triggerTermination(nowMs);
                    } else {
                        state_ = State::Safe;
                    }
                } else if (cmd == Command::Disarm) {
                    state_ = State::Safe;
                }
                break;

            case State::Triggered:
            case State::LatchedKill:
                HardwareInterlockDriver::setMotorKill(true);
                break;
        }
    }

    void triggerTermination(uint32_t nowMs) noexcept {
        state_ = State::Triggered;
        triggerStartMs_ = nowMs;
        HardwareInterlockDriver::setMotorKill(true);
    }

    static uint32_t computeCrc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1U)));
            }
        }
        return ~crc;
    }

    static uint64_t computeHmac(const RawPacket& pkt, uint64_t k1, uint64_t k2) noexcept {
        uint64_t h = k1 ^ (static_cast<uint64_t>(pkt.magic) << 32) ^ pkt.seq_num;
        h = (h ^ (static_cast<uint64_t>(pkt.timestamp_ms) << 16) ^ static_cast<uint32_t>(pkt.command)) * 0x517CC1B727220A95ULL;
        h ^= k2;
        h = (h ^ (h >> 32)) * 0x9E3779B97F4A7C15ULL;
        return h ^ (h >> 28);
    }

    State    state_{State::Safe};
    uint32_t lastValidSeq_{0};
    uint32_t armStartMs_{0};
    uint32_t triggerStartMs_{0};
    uint32_t spinStartMs_{0};
    bool     inSpinAnomaly_{false};
    uint64_t key1_{0};
    uint64_t key2_{0};
};

} // namespace fts::embedded
